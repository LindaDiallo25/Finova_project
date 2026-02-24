from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional

from finance_engine import GoalInput, evaluate_goal, GoalOutput

app = FastAPI(
    title="Finova Financial Calculation Engine",
    version="0.2.0",
    description="Deterministic engine for goal-based savings with realism & status.",
)


class GoalRequest(BaseModel):
    """
    JSON payload received from the front-end or bank system.
    """
    target_amount: float = Field(..., gt=0, description="Total amount the user wants to reach")
    months_to_target: int = Field(..., gt=0, description="Number of months to reach the goal")

    avg_monthly_saving: Optional[float] = Field(
        None, ge=0,
        description="Average monthly saving based on past behavior (optional for MVP)"
    )
    monthly_income: Optional[float] = Field(
        None, ge=0,
        description="User's monthly income (optional, used to assess realism)"
    )
    current_progress: Optional[float] = Field(
        0.0, ge=0,
        description="Amount already saved toward this specific goal"
    )


class GoalResponse(BaseModel):
    """
    JSON payload returned by the API.
    """
    required_monthly_saving: float
    predicted_completion_months: Optional[float]
    is_feasible_at_current_saving: Optional[bool]
    message: str

    feasibility_status: str
    realism_status: Optional[str]
    horizon: str


@app.get("/health")
def health_check():
    """
    Simple health check endpoint.
    Returns {"status": "ok"} if the service is up.
    """
    return {"status": "ok"}


@app.post("/calculate", response_model=GoalResponse)
def calculate_goal(request: GoalRequest):
    """
    Main API endpoint:
    - Accepts a goal description in JSON
    - Calls the financial engine
    - Returns the structured result (+ human message)
    """
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
