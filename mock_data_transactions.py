import random
import uuid
from datetime import datetime, timedelta

# --- CONFIGURATION CONSTANTS ---

MOCK_USER_ID = "bank_partner_user_42"

# Defined categories that the MVP's simple categorization logic (Sprint 2) will use.
CATEGORY_MAP = {
    'INCOME': 'Income',
    'HOUSING': 'Housing',
    'GROCERY': 'Groceries',
    'DINING': 'Dining Out',
    'TRANSPORT': 'Transportation',
    'UTILITIES': 'Utilities',
    'ENTERTAINMENT': 'Entertainment',
    'SAVINGS': 'Savings & Investment',
    'UNCATEGORIZED': 'Uncategorized',
}

# Merchant patterns for the simple categorization engine to test against (Sprint 2)
MERCHANT_PATTERNS = {
    CATEGORY_MAP['INCOME']: [
        ("PAYCHECK - ABC CORP", 4500.00, 500.00), # (Description, Mean Amount, Deviation)
        ("FREELANCE DEPOSIT", 800.00, 200.00),
    ],
    CATEGORY_MAP['HOUSING']: [
        ("RENT PAYMENT", 1800.00, 0.0),
    ],
    CATEGORY_MAP['UTILITIES']: [
        ("COMCAST INTERNET", 79.99, 5.0),
        ("GEICO AUTO INSURANCE", 125.00, 0.0),
        ("ELECTRIC BILL", 95.00, 30.0),
    ],
    CATEGORY_MAP['GROCERY']: [
        ("WHOLE FOODS", 65.00, 25.0),
        ("TRADER JOES", 45.00, 15.0),
        ("FARMERS MARKET", 30.00, 10.0),
    ],
    CATEGORY_MAP['DINING']: [
        ("STARBUCKS #453", 5.50, 1.5),
        ("DOMINOS PIZZA", 30.00, 5.0),
        ("LOCAL RESTAURANT", 55.00, 20.0),
    ],
    CATEGORY_MAP['ENTERTAINMENT']: [
        ("NETFLIX SUBSCRIPTION", 15.99, 0.0),
        ("AMZN* VIDEO RENTAL", 12.99, 5.0),
        ("BEST BUY ELECTRONICS", 250.00, 100.0),
    ],
    CATEGORY_MAP['TRANSPORT']: [
        ("UBER TRIP", 18.00, 10.0),
        ("LOCAL GAS STATION", 60.00, 5.0),
    ],
    CATEGORY_MAP['UNCATEGORIZED']: [ # Data to be categorized by the logic on Day 6
        ("EASYJET FLIGHT", 150.00, 50.0),
        ("PARKING LOT RECEIPT", 8.00, 2.0),
        ("DRY CLEANING 123", 25.50, 5.0),
        ("PET STORE PURCHASE", 35.00, 10.0),
    ]
}


# --- HELPER FUNCTIONS ---

def get_random_date(days_ago):
    """Returns a random datetime object within the last N days."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_ago)
    random_days = random.randint(0, days_ago)
    return start_date + timedelta(days=random_days)

def create_transaction_id():
    """Generates a unique ID for the Firestore document."""
    return str(uuid.uuid4())

# --- DATA GENERATION FUNCTIONS ---

def generate_transaction(category, description, mean_amount, deviation, days_ago):
    """
    Generates a single, realistic mock transaction document.
    """
    # Calculate a random amount near the mean
    amount = max(5.00, round(random.normalvariate(mean_amount, deviation), 2))
    
    # Determine type: Income is credit; everything else is debit.
    type_ = 'credit' if category == CATEGORY_MAP['INCOME'] else 'debit'

    return {
        'id': create_transaction_id(),
        'userId': MOCK_USER_ID,
        'type': type_,
        'rawDescription': description,
        'amount': amount,
        'date': get_random_date(days_ago).isoformat(), # ISO format for easy JSON/Firestore parsing
        # For the MVP, we pre-label most categories to test the UI/Goal logic immediately.
        'category': category,
    }

def generate_mock_transactions(days_of_history=60, num_transactions=40):
    """
    Generates a list of mock financial transactions for the last N days.
    """
    transactions = []
    
    # Create the recurring, high-value transactions
    transactions.append(generate_transaction(CATEGORY_MAP['HOUSING'], "RENT PAYMENT", 1800.00, 0, 5))
    transactions.append(generate_transaction(CATEGORY_MAP['INCOME'], "PAYCHECK - ABC CORP", 4500.00, 50.0, 1))
    transactions.append(generate_transaction(CATEGORY_MAP['INCOME'], "PAYCHECK - ABC CORP", 4500.00, 50.0, 30))
    transactions.append(generate_transaction(CATEGORY_MAP['SAVINGS'], "AUTOMATED SAVINGS TRANSFER", 500.00, 0, 1))

    # Generate random day-to-day transactions
    all_patterns = []
    for cat, patterns in MERCHANT_PATTERNS.items():
        all_patterns.extend([(cat, desc, mean, dev) for desc, mean, dev in patterns])
    
    for _ in range(num_transactions - len(transactions)):
        category, desc, mean, dev = random.choice(all_patterns)
        transactions.append(generate_transaction(category, desc, mean, dev, days_of_history))

    print(f"Generated {len(transactions)} mock transactions covering the last {days_of_history} days.")
    return transactions

def generate_mock_goals():
    """
    Generates an initial set of financial goals for the user.
    """
    goals = [
        {
            'id': 'goal_holiday_fund',
            'userId': MOCK_USER_ID,
            'name': 'European Holiday Fund',
            'targetAmount': 5000.00,
            'monthsToAchieve': 12,
            'startDate': datetime.now().isoformat(),
            # Calculate target date 12 months from now
            'targetDate': (datetime.now() + timedelta(days=365)).isoformat(),
            'currentProgress': 500.00, # Assume some progress has been made
            # This is the core metric the B2B2C widget focuses on:
            'requiredMonthlySaving': 416.67, # 5000 / 12 (simplified)
        },
        {
            'id': 'goal_down_payment',
            'userId': MOCK_USER_ID,
            'name': 'House Down Payment',
            'targetAmount': 40000.00,
            'monthsToAchieve': 60,
            'startDate': datetime.now().isoformat(),
            'targetDate': (datetime.now() + timedelta(days=365*5)).isoformat(),
            'currentProgress': 5000.00,
            'requiredMonthlySaving': 666.67, # 40000 / 60 (simplified)
        }
    ]
    print(f"Generated {len(goals)} mock goals.")
    return goals

# --- EXECUTION BLOCK ---

if __name__ == '__main__':
    print("--- Financial Data Generation Script ---")
    
    # 1. Generate Transactions
    mock_transactions = generate_mock_transactions()
    
    # 2. Generate Goals
    mock_goals = generate_mock_goals()
    
    print("\n--- Example Transaction Data (First 3) ---")
    import json
    # Use json.dumps for clean printing of the dictionary structure
    print(json.dumps(mock_transactions[:3], indent=2))
    
    print("\n--- Example Goal Data ---")
    print(json.dumps(mock_goals[0], indent=2))
    
    # NOTE 
    # This data can be uploaded directly to Firestore.
    # The 'rawDescription' field is what we will use for 
    # the keyword-based categorization in Sprint 2 (Day 6).