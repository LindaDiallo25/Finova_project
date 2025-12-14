from spending_engine import analyze_spending_and_goal
from finance_engine import GoalInput

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "data" / "personal_transactions.csv"


def main():
    # Define a sample goal for the user
    goal = GoalInput(
        target_amount=5000.0,
        months_to_target=12,
        avg_monthly_saving=None,   # will be inferred from income - forecast
        monthly_income=3000.0,
        current_progress=500.0,    # already saved
    )

    result = analyze_spending_and_goal(CSV_PATH, goal)

    print("=== GOAL ANALYSIS ===")
    print(f"Required monthly saving: {result.required_monthly_saving:.2f}")
    print(f"Engine horizon: {result.goal_output.horizon}")
    print(f"Feasibility status: {result.goal_output.feasibility_status}")
    print(f"Realism status: {result.goal_output.realism_status}")
    print()
    print("Narrative message from goal engine:")
    print(result.goal_output.message)
    print()

    print("=== EXPENSE FORECAST (LAST 6 MONTHS AVERAGE) ===")
    print(f"Projected total monthly expenses: {result.expense_forecast.projected_total_monthly_expenses:.2f}")
    print("By category:")
    for cf in result.expense_forecast.category_forecasts:
        disc = " (discretionary)" if cf.is_discretionary else ""
        print(f"  - {cf.category}: {cf.avg_monthly_spend:.2f}{disc}")

    print()
    print("=== SAVING GAP ===")
    print(f"Estimated net saving (income - projected expenses): {result.current_net_saving_estimate:.2f}")
    print(f"Required monthly saving (from goal engine): {result.required_monthly_saving:.2f}")
    print(f"Gap to close: {result.saving_gap:.2f}")
    print()

    if not result.recommendations:
        print("You are already saving enough at your current expense level to meet this goal.")
    else:
        print("=== RECOMMENDATIONS TO CLOSE THE GAP ===")
        for rec in result.recommendations:
            print(
                f"- Cut '{rec.category}' from {rec.current_monthly_spend:.2f} "
                f"to {rec.suggested_new_monthly_spend:.2f} per month "
                f"(frees {rec.monthly_saving:.2f} per month)."
            )


if __name__ == "__main__":
    main()
