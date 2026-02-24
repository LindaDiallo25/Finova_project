from datetime import datetime
from typing import List, Dict

from mock_data_transactions import generate_mock_transactions, generate_mock_goals
from finance_engine import GoalInput, evaluate_goal


def compute_avg_monthly_saving(transactions: List[Dict]) -> float:
    """
    Simple heuristic:
    - income = sum of credits
    - expenses = sum of debits
    - net saving = income - expenses
    - avg monthly saving = net saving / number of months

    This is just for MVP testing.
    """
    if not transactions:
        return 0.0

    dates = [datetime.fromisoformat(t["date"]) for t in transactions]
    min_date = min(dates)
    max_date = max(dates)

    days_span = max((max_date - min_date).days, 1)
    approx_months = max(days_span / 30.0, 1 / 30.0)

    income = sum(t["amount"] for t in transactions if t["type"] == "credit")
    expenses = sum(t["amount"] for t in transactions if t["type"] == "debit")

    net_saving = income - expenses
    avg_monthly_saving = net_saving / approx_months

    return max(avg_monthly_saving, 0.0)


def main():
    print("--- Testing Financial Engine with Mock Data ---")

    transactions = generate_mock_transactions(days_of_history=60, num_transactions=40)
    goals = generate_mock_goals()

    test_goal = goals[0]

    print(f"Using goal: {test_goal['name']}")
    print(f"Target amount: {test_goal['targetAmount']}")
    print(f"Months to achieve: {test_goal['monthsToAchieve']}")

    avg_monthly_saving = compute_avg_monthly_saving(transactions)
    print(f"Computed average monthly saving from mock transactions: {avg_monthly_saving:.2f}")

    goal_input = GoalInput(
        target_amount=test_goal["targetAmount"],
        months_to_target=test_goal["monthsToAchieve"],
        avg_monthly_saving=avg_monthly_saving,
    )

    result = evaluate_goal(goal_input)

    print("\n--- Engine Output ---")
    print(f"Required monthly saving: {result.required_monthly_saving:.2f}")
    if result.predicted_completion_months is not None:
        print(f"Predicted completion (months): {result.predicted_completion_months:.1f}")
    print(f"Feasible at current saving pace?: {result.is_feasible_at_current_saving}")
    print(f"Message:\n{result.message}")


if __name__ == "__main__":
    main()
