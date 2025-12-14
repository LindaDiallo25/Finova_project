from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

from finance_engine import GoalInput, GoalOutput, evaluate_goal


# =========================
# CONFIG (MVP)
# =========================

DEFAULT_MONTHS_BACK = 6

# Categories that often represent transfers, repayments, or non-consumption flows.
# These can double-count spending if included (e.g., you already have the underlying restaurant/shopping spend).
EXCLUDED_CATEGORIES_EXACT = {
    "Credit Card Payment",
    "Transfer",
    "Transfers",
    "Balance Transfer",
    "Internal Transfer",
}

# Some exports label transfers differently; we also exclude by keyword.
EXCLUDED_CATEGORY_KEYWORDS = {
    "credit card payment",
    "transfer",
    "payment - credit card",
    "cc payment",
    "balance transfer",
}

# Heuristic discretionary labeling for MVP.
# Later you will replace this with ML/Vertex AI classification.
DISCRETIONARY_KEYWORDS = {
    "restaurants",
    "coffee",
    "bars",
    "alcohol",
    "shopping",
    "electronics",
    "music",
    "movies",
    "entertainment",
    "travel",
    "vacation",
    "subscriptions",
}

# Optional: treat these as fixed-ish (not used heavily yet, but useful for future messaging).
FIXED_KEYWORDS = {
    "rent",
    "mortgage",
    "utilities",
    "insurance",
    "internet",
    "phone",
    "electric",
}


# =========================
# DATA MODELS
# =========================

@dataclass
class CategoryBreakdownRow:
    category: str
    avg_monthly_spend: float
    pct_of_total: float
    is_discretionary: bool


@dataclass
class ExpenseForecastResult:
    months_used: int
    projected_total_monthly_expenses: float
    breakdown: List[CategoryBreakdownRow]


@dataclass
class SavingRecommendation:
    category: str
    current_monthly_spend: float
    suggested_new_monthly_spend: float
    monthly_saving: float


@dataclass
class SpendingGoalAnalysis:
    goal_output: GoalOutput
    expense_forecast: ExpenseForecastResult

    # Derived behavior metrics
    estimated_avg_monthly_saving: float

    # Goal requirement & gap
    required_monthly_saving: float
    saving_gap: float

    # Suggestions to close the gap
    recommendations: List[SavingRecommendation]


# =========================
# PATH UTIL
# =========================

def resolve_repo_relative_path(relative_path: str) -> str:
    """
    Resolve a path relative to this file's directory.
    This makes the code portable for any user cloning the repo.
    """
    base_dir = Path(__file__).resolve().parent
    return str(base_dir / relative_path)


# =========================
# CLEANING / CLASSIFICATION HELPERS
# =========================

def _normalize_category(raw_category: object) -> str:
    if not isinstance(raw_category, str):
        return "Other"
    cat = raw_category.strip()
    return cat if cat else "Other"


def _category_is_excluded(category: str) -> bool:
    cat_norm = category.strip()
    if cat_norm in EXCLUDED_CATEGORIES_EXACT:
        return True

    cat_lower = cat_norm.lower()
    return any(k in cat_lower for k in EXCLUDED_CATEGORY_KEYWORDS)


def _is_discretionary(category: str) -> bool:
    cat_lower = category.lower()
    return any(k in cat_lower for k in DISCRETIONARY_KEYWORDS)


def _is_fixed(category: str) -> bool:
    cat_lower = category.lower()
    return any(k in cat_lower for k in FIXED_KEYWORDS)


# =========================
# DATA LOADING
# =========================

def load_and_preprocess_transactions(csv_path: str) -> pd.DataFrame:
    """
    Expected columns (from your CSV):
      - Date
      - Description
      - Amount
      - Transaction Type  (credit/debit)
      - Category
      - Account Name

    Returns: cleaned expenses-only dataframe with:
      - Date (datetime)
      - Amount (float)
      - CategoryNorm (string)
      - YearMonth (YYYY-MM)
    """
    df = pd.read_csv(csv_path)

    # Parse date
    if "Date" not in df.columns:
        raise ValueError("CSV must include a 'Date' column.")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce", dayfirst=True)
    df = df.dropna(subset=["Date"]).copy()

    # Keep only debits (expenses)
    if "Transaction Type" not in df.columns:
        raise ValueError("CSV must include a 'Transaction Type' column.")
    df = df[df["Transaction Type"].astype(str).str.lower().str.strip() == "debit"].copy()

    # Amount must exist
    if "Amount" not in df.columns:
        raise ValueError("CSV must include an 'Amount' column.")
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    df = df.dropna(subset=["Amount"]).copy()

    # Normalize category
    if "Category" not in df.columns:
        # If missing, create generic category
        df["CategoryNorm"] = "Other"
    else:
        df["CategoryNorm"] = df["Category"].apply(_normalize_category)

    # Exclude categories that are transfers/repayments (to avoid double counting)
    df = df[~df["CategoryNorm"].apply(_category_is_excluded)].copy()

    # Build YearMonth key
    df["YearMonth"] = df["Date"].dt.to_period("M").astype(str)

    return df


# =========================
# FORECASTING (MVP)
# =========================

def compute_month_window(df: pd.DataFrame, months_back: int) -> pd.DataFrame:
    """
    Keeps only last N months based on max Date.
    """
    if df.empty:
        return df

    df = df.copy()
    df["YearMonthPeriod"] = df["Date"].dt.to_period("M").dt.to_timestamp()
    max_month = df["YearMonthPeriod"].max()
    min_month = (max_month - pd.DateOffset(months=months_back - 1)).to_period("M").to_timestamp()

    return df[(df["YearMonthPeriod"] >= min_month) & (df["YearMonthPeriod"] <= max_month)].copy()


def forecast_monthly_expenses(df: pd.DataFrame, months_back: int = DEFAULT_MONTHS_BACK) -> ExpenseForecastResult:
    """
    MVP forecast = average monthly spend per category over the last N months.
    Returns totals and chart-ready breakdown (with %).
    """
    if df.empty:
        return ExpenseForecastResult(months_used=0, projected_total_monthly_expenses=0.0, breakdown=[])

    recent = compute_month_window(df, months_back=months_back)
    if recent.empty:
        return ExpenseForecastResult(months_used=0, projected_total_monthly_expenses=0.0, breakdown=[])

    # Total spend per month per category
    monthly_cat = (
        recent.groupby(["YearMonth", "CategoryNorm"])["Amount"]
        .sum()
        .reset_index()
    )

    months_used = monthly_cat["YearMonth"].nunique()
    months_used = max(months_used, 1)

    # Average monthly spend per category
    cat_avg = (
        monthly_cat.groupby("CategoryNorm")["Amount"]
        .sum()
        .div(months_used)
        .reset_index()
        .rename(columns={"Amount": "AvgMonthlySpend"})
    )

    total = float(cat_avg["AvgMonthlySpend"].sum())
    total = max(total, 0.0)

    breakdown: List[CategoryBreakdownRow] = []
    for _, row in cat_avg.iterrows():
        cat = str(row["CategoryNorm"])
        avg = float(row["AvgMonthlySpend"])
        pct = (avg / total) if total > 0 else 0.0
        breakdown.append(
            CategoryBreakdownRow(
                category=cat,
                avg_monthly_spend=avg,
                pct_of_total=pct,
                is_discretionary=_is_discretionary(cat),
            )
        )

    # Sort breakdown by spend desc (useful for charts)
    breakdown.sort(key=lambda x: x.avg_monthly_spend, reverse=True)

    return ExpenseForecastResult(
        months_used=months_used,
        projected_total_monthly_expenses=total,
        breakdown=breakdown,
    )


# =========================
# RECOMMENDATIONS (GOAL-DRIVEN)
# =========================

def build_cut_recommendations(
    breakdown: List[CategoryBreakdownRow],
    gap_to_close: float,
    max_categories: int = 4,
    max_cut_ratio_per_category: float = 0.30,
    min_category_size: float = 20.0,
) -> List[SavingRecommendation]:
    """
    Suggests cuts to discretionary categories to close the gap.

    - Only considers discretionary categories
    - Prioritizes biggest categories
    - Caps cut ratio per category (e.g. max 30%)
    - Skips tiny categories (to avoid silly recommendations like cutting $1 coffee)
    """
    if gap_to_close <= 0:
        return []

    discretionary = [b for b in breakdown if b.is_discretionary and b.avg_monthly_spend >= min_category_size]
    discretionary.sort(key=lambda x: x.avg_monthly_spend, reverse=True)

    recommendations: List[SavingRecommendation] = []
    remaining = gap_to_close

    for b in discretionary[:max_categories]:
        if remaining <= 0:
            break

        current = b.avg_monthly_spend
        max_cut = current * max_cut_ratio_per_category
        cut = min(max_cut, remaining)

        new_spend = max(current - cut, 0.0)

        recommendations.append(
            SavingRecommendation(
                category=b.category,
                current_monthly_spend=current,
                suggested_new_monthly_spend=new_spend,
                monthly_saving=cut,
            )
        )
        remaining -= cut

    return recommendations


# =========================
# MAIN ORCHESTRATOR
# =========================

def analyze_spending_and_goal(
    csv_path: str,
    goal: GoalInput,
    months_back: int = DEFAULT_MONTHS_BACK
) -> SpendingGoalAnalysis:
    """
    Full MVP flow:
      1) Load & clean transactions
      2) Forecast monthly expenses from last N months
      3) Estimate avg monthly saving = income - forecast expenses
      4) Feed avg saving into goal engine (so feasibility is not "unknown")
      5) Compute gap and propose category cuts if needed
    """
    if goal.monthly_income is None or goal.monthly_income <= 0:
        raise ValueError("GoalInput.monthly_income must be provided and > 0.")

    df = load_and_preprocess_transactions(csv_path)
    forecast = forecast_monthly_expenses(df, months_back=months_back)

    # Behavioral saving estimate (MVP)
    estimated_saving = goal.monthly_income - forecast.projected_total_monthly_expenses
    estimated_saving = max(float(estimated_saving), 0.0)

    # Feed behavior into the goal engine so feasibility is meaningful
    enriched_goal = GoalInput(
        target_amount=goal.target_amount,
        months_to_target=goal.months_to_target,
        avg_monthly_saving=estimated_saving,
        monthly_income=goal.monthly_income,
        current_progress=goal.current_progress,
    )

    goal_output = evaluate_goal(enriched_goal)

    required = float(goal_output.required_monthly_saving)
    gap = max(required - estimated_saving, 0.0)

    recommendations = build_cut_recommendations(
        breakdown=forecast.breakdown,
        gap_to_close=gap,
    )

    return SpendingGoalAnalysis(
        goal_output=goal_output,
        expense_forecast=forecast,
        estimated_avg_monthly_saving=estimated_saving,
        required_monthly_saving=required,
        saving_gap=gap,
        recommendations=recommendations,
    )


# =========================
# OPTIONAL: CONVENIENCE RUNNER
# =========================

def run_local_demo():
    """
    Quick local demo runner (optional).
    """
    csv_path = resolve_repo_relative_path("data/personal_transactions.csv")

    # Example goal
    goal = GoalInput(
        target_amount=5000.0,
        months_to_target=12,
        monthly_income=3000.0,
        current_progress=500.0,
        avg_monthly_saving=None,  # will be inferred
    )

    result = analyze_spending_and_goal(csv_path, goal)

    print("=== GOAL ENGINE OUTPUT ===")
    print(f"Required monthly saving: {result.required_monthly_saving:.2f}")
    print(f"Estimated avg saving (income - forecasted expenses): {result.estimated_avg_monthly_saving:.2f}")
    print(f"Feasibility: {result.goal_output.feasibility_status}")
    print(f"Realism: {result.goal_output.realism_status}")
    print(f"Horizon: {result.goal_output.horizon}")
    print()
    print(result.goal_output.message)
    print()

    print("=== EXPENSE BREAKDOWN (Chart-ready) ===")
    total = result.expense_forecast.projected_total_monthly_expenses
    print(f"Projected total monthly expenses: {total:.2f} (months used: {result.expense_forecast.months_used})")
    for row in result.expense_forecast.breakdown[:10]:
        disc = "discretionary" if row.is_discretionary else "non-discretionary"
        print(f"- {row.category:25s} {row.avg_monthly_spend:8.2f}  ({row.pct_of_total*100:5.1f}%)  [{disc}]")

    print()
    print(f"Saving gap to close: {result.saving_gap:.2f}")

    if not result.recommendations:
        print("No cuts needed — current forecasted spending supports the goal.")
    else:
        print("=== RECOMMENDED CUTS ===")
        for rec in result.recommendations:
            print(
                f"- {rec.category}: {rec.current_monthly_spend:.2f} -> {rec.suggested_new_monthly_spend:.2f} "
                f"(save {rec.monthly_saving:.2f}/month)"
            )


if __name__ == "__main__":
    run_local_demo()
