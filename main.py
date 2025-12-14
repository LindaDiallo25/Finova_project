from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional, List

from finance_engine import GoalInput, evaluate_goal, GoalOutput
from spending_engine import (
    analyze_spending_and_goal,
    forecast_monthly_expenses,
    load_and_preprocess_transactions,
    resolve_repo_relative_path,
)

app = FastAPI(
    title="Finova Financial & Spending Engine",
    version="0.3.0",
    description="MVP APIs for goal calculations + transaction forecasting + recommendations.",
)


# =========================
# EXISTING: GOAL ENGINE API
# =========================

class GoalRequest(BaseModel):
    target_amount: float = Field(..., gt=0)
    months_to_target: int = Field(..., gt=0)
    avg_monthly_saving: Optional[float] = Field(None, ge=0)
    monthly_income: Optional[float] = Field(None, ge=0)
    current_progress: Optional[float] = Field(0.0, ge=0)


class GoalResponse(BaseModel):
    required_monthly_saving: float
    predicted_completion_months: Optional[float]
    is_feasible_at_current_saving: Optional[bool]
    message: str
    feasibility_status: str
    realism_status: Optional[str]
    horizon: str


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/calculate", response_model=GoalResponse)
def calculate_goal(request: GoalRequest):
    goal_input = GoalInput(
        target_amount=request.target_amount,
        months_to_target=request.months_to_target,
        avg_monthly_saving=request.avg_monthly_saving,
        monthly_income=request.monthly_income,
        current_progress=request.current_progress or 0.0,
    )

    result: GoalOutput = evaluate_goal(goal_input)

    return GoalResponse(
        required_monthly_saving=result.required_monthly_saving,
        predicted_completion_months=result.predicted_completion_months,
        is_feasible_at_current_saving=result.is_feasible_at_current_saving,
        message=result.message,
        feasibility_status=result.feasibility_status,
        realism_status=result.realism_status,
        horizon=result.horizon,
    )


# =========================
# NEW: SPENDING ENGINE API
# =========================

class SpendingAnalyzeRequest(BaseModel):
    """
    Request body used by the widget.
    For MVP we let you pass either:
      - csv_relative_path (repo-relative) OR
      - default sample data under data/personal_transactions.csv
    """
    target_amount: float = Field(..., gt=0)
    months_to_target: int = Field(..., gt=0)
    monthly_income: float = Field(..., gt=0)

    current_progress: float = Field(0.0, ge=0)
    months_back: int = Field(6, gt=0, le=24)

    csv_relative_path: Optional[str] = Field(
        "data/personal_transactions.csv",
        description="Repo-relative path to CSV (default: data/personal_transactions.csv)"
    )


class BreakdownRowResponse(BaseModel):
    category: str
    avg_monthly_spend: float
    pct_of_total: float
    is_discretionary: bool


class SpendingForecastResponse(BaseModel):
    months_used: int
    projected_total_monthly_expenses: float
    breakdown: List[BreakdownRowResponse]


class RecommendationResponse(BaseModel):
    category: str
    current_monthly_spend: float
    suggested_new_monthly_spend: float
    monthly_saving: float


class SpendingAnalyzeResponse(BaseModel):
    # Goal engine output
    required_monthly_saving: float
    predicted_completion_months: Optional[float]
    is_feasible_at_current_saving: Optional[bool]
    message: str
    feasibility_status: str
    realism_status: Optional[str]
    horizon: str

    # Spending forecast
    forecast: SpendingForecastResponse

    # Derived behavioral saving estimate
    estimated_avg_monthly_saving: float

    # Gap + recommended cuts
    saving_gap: float
    recommendations: List[RecommendationResponse]


@app.post("/spending/forecast", response_model=SpendingForecastResponse)
def spending_forecast(request: SpendingAnalyzeRequest):
    """
    Lightweight endpoint:
    - loads CSV
    - produces chart-ready breakdown + total forecast
    """
    csv_path = resolve_repo_relative_path(request.csv_relative_path or "data/personal_transactions.csv")

    df = load_and_preprocess_transactions(csv_path)
    fc = forecast_monthly_expenses(df, months_back=request.months_back)

    return SpendingForecastResponse(
        months_used=fc.months_used,
        projected_total_monthly_expenses=fc.projected_total_monthly_expenses,
        breakdown=[
            BreakdownRowResponse(
                category=row.category,
                avg_monthly_spend=row.avg_monthly_spend,
                pct_of_total=row.pct_of_total,
                is_discretionary=row.is_discretionary,
            )
            for row in fc.breakdown
        ],
    )


@app.post("/spending/analyze", response_model=SpendingAnalyzeResponse)
def spending_analyze(request: SpendingAnalyzeRequest):
    """
    Full endpoint for the widget:
    - forecast expenses
    - estimate behavioral saving
    - run goal engine with that behavior
    - compute gap vs schedule
    - suggest cuts (recommendations)
    """
    csv_path = resolve_repo_relative_path(request.csv_relative_path or "data/personal_transactions.csv")

    goal = GoalInput(
        target_amount=request.target_amount,
        months_to_target=request.months_to_target,
        monthly_income=request.monthly_income,
        current_progress=request.current_progress,
        avg_monthly_saving=None,  # spending engine will infer behavior from forecast
    )

    result = analyze_spending_and_goal(csv_path, goal, months_back=request.months_back)

    # Build forecast response
    forecast_resp = SpendingForecastResponse(
        months_used=result.expense_forecast.months_used,
        projected_total_monthly_expenses=result.expense_forecast.projected_total_monthly_expenses,
        breakdown=[
            BreakdownRowResponse(
                category=row.category,
                avg_monthly_spend=row.avg_monthly_spend,
                pct_of_total=row.pct_of_total,
                is_discretionary=row.is_discretionary,
            )
            for row in result.expense_forecast.breakdown
        ],
    )

    return SpendingAnalyzeResponse(
        required_monthly_saving=result.goal_output.required_monthly_saving,
        predicted_completion_months=result.goal_output.predicted_completion_months,
        is_feasible_at_current_saving=result.goal_output.is_feasible_at_current_saving,
        message=result.goal_output.message,
        feasibility_status=result.goal_output.feasibility_status,
        realism_status=result.goal_output.realism_status,
        horizon=result.goal_output.horizon,

        forecast=forecast_resp,
        estimated_avg_monthly_saving=result.estimated_avg_monthly_saving,
        saving_gap=result.saving_gap,
        recommendations=[
            RecommendationResponse(
                category=r.category,
                current_monthly_spend=r.current_monthly_spend,
                suggested_new_monthly_spend=r.suggested_new_monthly_spend,
                monthly_saving=r.monthly_saving,
            )
            for r in result.recommendations
        ],
    )

