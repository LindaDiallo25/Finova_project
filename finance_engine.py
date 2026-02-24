from dataclasses import dataclass
from typing import Optional


# --- CONFIG / CONSTANTS ---

FEASIBILITY_MARGIN = 1.10  # 10% above required saving = "comfortable"
SHORT_TERM_MAX_MONTHS = 6
MEDIUM_TERM_MAX_MONTHS = 36


# --- DATA CLASSES ---

@dataclass
class GoalInput:
    """
    Input for the financial engine.
    """
    target_amount: float                  # Total goal amount (e.g. 5000.0)
    months_to_target: int                 # Planned months to reach the goal (e.g. 12)
    avg_monthly_saving: Optional[float] = None   # Avg saving from behavior analysis
    monthly_income: Optional[float] = None       # Optional: user monthly income
    current_progress: float = 0.0                # Amount already saved toward this goal


@dataclass
class GoalOutput:
    """
    Output returned by the financial engine.
    """
    required_monthly_saving: float
    predicted_completion_months: Optional[float]
    is_feasible_at_current_saving: Optional[bool]
    message: str

    # Enhanced, structured signals for UI / analytics
    feasibility_status: str               # "unknown" | "on_track_comfortable" | "on_track_tight" | "behind"
    realism_status: Optional[str]         # None | "unrealistic" | "very_hard" | "realistic"
    horizon: str                          # "short_term" | "medium_term" | "long_term"


# --- CORE UTILS ---

def classify_horizon(months_to_target: int) -> str:
    if months_to_target <= SHORT_TERM_MAX_MONTHS:
        return "short_term"
    elif months_to_target <= MEDIUM_TERM_MAX_MONTHS:
        return "medium_term"
    else:
        return "long_term"


def calculate_required_monthly_saving(
    target_amount: float,
    months_to_target: int,
    current_progress: float = 0.0
) -> float:
    """
    required monthly saving = max(target_amount - current_progress, 0) / months_to_target
    """
    if months_to_target <= 0:
        raise ValueError("months_to_target must be > 0")

    remaining = max(target_amount - current_progress, 0.0)
    return remaining / months_to_target


def predict_completion_months(
    target_amount: float,
    current_progress: float,
    avg_monthly_saving: Optional[float]
) -> Optional[float]:
    """
    Very simple prediction for MVP:
    - If avg_monthly_saving <= 0 or None → return None (can't estimate).
    - Else months = remaining_amount / avg_monthly_saving
    """
    remaining = max(target_amount - current_progress, 0.0)

    if avg_monthly_saving is None or avg_monthly_saving <= 0:
        return None

    return remaining / avg_monthly_saving


def classify_realism(
    required_monthly_saving: float,
    monthly_income: Optional[float]
) -> Optional[str]:
    """
    Classify how realistic the goal is relative to income.
    """
    if monthly_income is None or monthly_income <= 0:
        return None

    ratio = required_monthly_saving / monthly_income

    if ratio > 1.0:
        return "unrealistic"
    elif ratio > 0.6:
        return "very_hard"
    else:
        return "realistic"


def classify_feasibility(
    required_monthly_saving: float,
    avg_monthly_saving: Optional[float]
) -> tuple[Optional[bool], str]:
    """
    Returns (is_feasible, feasibility_status).
    feasibility_status:
      - "unknown" if we don't know avg saving
      - "on_track_comfortable" if avg >= required * margin
      - "on_track_tight" if avg >= required but < required * margin
      - "behind" otherwise
    """
    if avg_monthly_saving is None:
        return None, "unknown"

    if avg_monthly_saving >= required_monthly_saving * FEASIBILITY_MARGIN:
        return True, "on_track_comfortable"
    elif avg_monthly_saving >= required_monthly_saving:
        return True, "on_track_tight"
    else:
        return False, "behind"


# --- MAIN ORCHESTRATION FUNCTION ---

def evaluate_goal(goal: GoalInput) -> GoalOutput:
    """
    Main orchestration logic combining:
    - deterministic required saving
    - feasibility classification
    - realism vs income
    - horizon classification
    - simple prediction for completion
    - a human-readable narrative message
    """

    horizon = classify_horizon(goal.months_to_target)

    required = calculate_required_monthly_saving(
        target_amount=goal.target_amount,
        months_to_target=goal.months_to_target,
        current_progress=goal.current_progress,
    )

    predicted_completion = predict_completion_months(
        target_amount=goal.target_amount,
        current_progress=goal.current_progress,
        avg_monthly_saving=goal.avg_monthly_saving,
    )

    is_feasible, feasibility_status = classify_feasibility(
        required_monthly_saving=required,
        avg_monthly_saving=goal.avg_monthly_saving
    )

    realism_status = classify_realism(
        required_monthly_saving=required,
        monthly_income=goal.monthly_income
    )

    # Build narrative message
    message_parts: list[str] = []

    # Base description
    message_parts.append(
        f"You want to reach a goal of {goal.target_amount:.2f} in {goal.months_to_target} months "
        f"({horizon.replace('_', ' ')})."
    )

    if goal.current_progress > 0:
        message_parts.append(
            f"You have already saved {goal.current_progress:.2f}, "
            f"so the remaining amount is approximately {max(goal.target_amount - goal.current_progress, 0.0):.2f}."
        )

    message_parts.append(
        f"To stay on track, you need to save about {required:.2f} per month from now on."
    )

    # Realism, if income is known
    if realism_status is not None and goal.monthly_income is not None:
        if realism_status == "unrealistic":
            message_parts.append(
                f"This goal is unrealistic at your current income of {goal.monthly_income:.2f}, "
                f"because the required saving exceeds your monthly income."
            )
        elif realism_status == "very_hard":
            message_parts.append(
                f"This goal is very demanding, as the required saving represents a large share of your "
                f"monthly income ({required / goal.monthly_income:.0%})."
            )
        elif realism_status == "realistic":
            message_parts.append(
                "Relative to your income, this goal is challenging but realistic if you maintain discipline."
            )

    # Behavior-based prediction
    if goal.avg_monthly_saving is not None:
        if predicted_completion is None or goal.avg_monthly_saving <= 0:
            message_parts.append(
                "You are currently not saving any money on average, "
                "so we cannot reliably estimate when you would reach this goal. "
                "Start by setting aside even a small fixed amount each month."
            )
        else:
            message_parts.append(
                f"Based on your current average saving of {goal.avg_monthly_saving:.2f} per month, "
                f"you are likely to reach the goal in around {predicted_completion:.1f} months."
            )

            if feasibility_status == "on_track_comfortable":
                message_parts.append(
                    "You are comfortably on track to meet or even exceed your target on time."
                )
            elif feasibility_status == "on_track_tight":
                message_parts.append(
                    "You are technically on track, but your margin is small: any overspending may delay the goal."
                )
            elif feasibility_status == "behind":
                message_parts.append(
                    "At your current saving pace, you are behind your plan. "
                    "You may need to increase your monthly saving or extend the timeline."
                )

    else:
        message_parts.append(
            "We do not yet have enough data about your current saving behavior to estimate your real pace. "
            "Once we analyze your transactions, we will show whether you are ahead or behind schedule."
        )

    full_message = " ".join(message_parts)

    return GoalOutput(
        required_monthly_saving=required,
        predicted_completion_months=predicted_completion,
        is_feasible_at_current_saving=is_feasible,
        message=full_message,
        feasibility_status=feasibility_status,
        realism_status=realism_status,
        horizon=horizon,
    )
