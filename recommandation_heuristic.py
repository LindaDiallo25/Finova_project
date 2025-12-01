"""
Finova MVP Recommendation Engine (Phase I: Heuristic Logic)

This is the initial, deterministic, rule-based recommendation engine for the MVP.
It relies solely on simple conditional logic (if/then) and current data inputs.

"""

from decimal import Decimal, ROUND_HALF_UP
import functions_framework
import json
from typing import Optional

# --- Constants for Financial Precision ---
D = Decimal
TWO_PLACES = D('0.01')
D_ZERO = D('0.00')

def generate_recommendation_heuristic_core(
    saving_deficit: float,
    top_discretionary_category: str,
    top_discretionary_amount: float,
    fixed_expenses_ratio: float,
    has_lump_sum: bool = False
) -> str:
    """
    Core function: Generates a recommendation based on simple heuristic rules.

    Args:
        saving_deficit: The difference needed to meet the goal (Positive=Deficit, Negative=Surplus).
        top_discretionary_category: The largest non-essential spending category (e.g., 'Dining Out').
        top_discretionary_amount: The amount spent in that top category.
        fixed_expenses_ratio: Ratio of fixed expenses to income (0.0 to 1.0).
        has_lump_sum: Flag indicating a recent large, temporary income spike.

    Returns:
        A prioritized, actionable recommendation string.
    """
    
    try:
        # Convert all floats to Decimal for guaranteed financial accuracy
        deficit = D(str(saving_deficit)).quantize(TWO_PLACES)
        top_spend = D(str(top_discretionary_amount)).quantize(TWO_PLACES)
        fixed_ratio = D(str(fixed_expenses_ratio))
    except InvalidOperation:
        return "ERROR: Invalid numeric input provided to the core calculator."

    # --- Rule Set 2: On Track/Ahead Actions (Prioritized: Look for windfall first) ---
    
    # R2.3: Reinvest Savings - Check for a recent lump sum (highest priority action)
    if has_lump_sum:
        # Suggesting a fixed amount for simplicity in Phase I
        return (
            "WINDFALL DETECTED: We noticed a recent temporary income spike. "
            "Applying **$300** of this towards your goal could significantly accelerate your completion date!"
        )
        
    if deficit <= D_ZERO: # User is on track or ahead (Surplus = deficit * -1)
        surplus = deficit * D('-1') 
        
        # R2.2: Accelerate Goal - Large surplus suggests early achievement is possible.
        if surplus > D_ZERO and surplus >= D('50.00'):
            # Note: The "2 months early" figure is a static heuristic placeholder for MVP
            return (
                f"FANTASTIC WORK! Your current saving pace has a **${surplus.quantize(TWO_PLACES)}** surplus. "
                "You are on track to hit your goal **2 months early**! Keep going or consider increasing your goal target."
            )

        # R2.1: Maintain Success - Small surplus or exactly on track.
        else:
            return (
                "GREAT JOB! You are currently on track to hit your goal on time. "
                "We recommend maintaining your current saving habits."
            )

    # --- Rule Set 1: Addressing a Deficit (Priority 2) ---
    elif deficit > D_ZERO:
        
        # R1.1: Core Cut - Can the deficit be covered by cutting the top discretionary spend?
        if top_spend >= deficit:
            # Round deficit cut to nearest dollar for simplicity in the recommendation message
            cut_amount = deficit.quantize(D('1'), rounding=ROUND_HALF_UP)
            return (
                f"ACTION NEEDED: Your predicted saving deficit is ${deficit.quantize(TWO_PLACES)}. "
                f"Try to reduce your **{top_discretionary_category}** budget by **${cut_amount}** this month to get back on track."
            )
        
        # R1.2: Budget Review - Cutting the top category isn't enough.
        elif top_spend < deficit and deficit <= D('200.00'):
            remaining_cut = (deficit - top_spend).quantize(TWO_PLACES)
            return (
                f"ACTION NEEDED: You need an extra ${deficit.quantize(TWO_PLACES)} this month. Reducing {top_discretionary_category} by ${top_spend.quantize(TWO_PLACES)} still leaves a gap of ${remaining_cut}. "
                f"We recommend reviewing all **non-essential** spending this week to close the gap."
            )
        
        # R1.3: Aggressive Goal - The goal might be too ambitious given the fixed expense ratio.
        elif fixed_ratio >= D('0.60') and deficit > D('150.00'):
            # Simple heuristic: 1 month extension for every $50 deficit, minimum 2 months
            extension_months = max(2, int(deficit / D('50.00')))
            ratio_percent = (fixed_ratio * D('100')).quantize(D('1'))
            return (
                f"GOAL REVIEW: Your required saving is aggressive ({ratio_percent}% fixed expenses). "
                f"Consider extending your goal timeline by **{extension_months} months** for a more manageable monthly saving."
            )
    
    # Fallback in case of unexpected zero values or error state
    return "Check back soon for more specific personalized advice!"

# --- Cloud Function HTTP Entry Point ---

@functions_framework.http
def generate_recommendation_heuristic_api(request):
    """
    HTTP Cloud Function wrapper for the recommendation engine.
    """
    # Set CORS headers for the main request
    headers = { 'Access-Control-Allow-Origin': '*' }
    
    # Handle CORS preflight request
    if request.method == 'OPTIONS':
        headers['Access-Control-Allow-Methods'] = 'POST'
        headers['Access-Control-Allow-Headers'] = 'Content-Type'
        headers['Access-Control-Max-Age'] = '3600'
        return ('', 204, headers)

    try:
        request_json = request.get_json(silent=True)
        if not request_json:
            raise ValueError("Invalid JSON payload or missing data.")

        # Extract parameters from the request payload
        recommendation_text = generate_recommendation_heuristic_core(
            saving_deficit=request_json.get('savingDeficit', 0.0),
            top_discretionary_category=request_json.get('topDiscretionaryCategory', 'Discretionary Spending'),
            top_discretionary_amount=request_json.get('topDiscretionaryAmount', 0.0),
            fixed_expenses_ratio=request_json.get('fixedExpensesRatio', 0.0),
            has_lump_sum=request_json.get('hasLumpSum', False)
        )
        
        response_data = {
            "recommendation": recommendation_text,
            "status": "success",
            "source": "MVP Heuristics (Phase I)"
        }
        return (json.dumps(response_data), 200, headers)

    except Exception as e:
        error_message = f"Server Error during heuristic calculation: {str(e)}"
        print(error_message)
        response_data = {
            "recommendation": "We are unable to provide a recommendation at this time.",
            "status": "error"
        }
        return (json.dumps(response_data), 500, headers)