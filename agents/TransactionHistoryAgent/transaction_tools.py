from langchain.tools import tool

@tool
def get_recent_transactions(user_id) -> dict:
    """
    Fetch last 5 transactions across all user accounts.
    Returns type, amount, and date for each transaction.
    """

    transaction_history = [
        {"type": "debit", "amount": 2500, "date": "2025-07-17"},
        {"type": "credit", "amount": 15000, "date": "2025-07-16"},
        {"type": "debit", "amount": 1000, "date": "2025-07-15"},
        {"type": "credit", "amount": 32000, "date": "2025-07-14"},
        {"type": "debit", "amount": 200, "date": "2025-07-13"},
        {"type": "debit", "amount": 1000, "date": "2025-07-15"},
        {"type": "credit", "amount": 32000, "date": "2025-07-14"},
        {"type": "debit", "amount": 200, "date": "2025-07-13"}
    ]
    return transaction_history