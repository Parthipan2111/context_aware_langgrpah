from langchain.tools import tool

@tool
def get_recent_transactions(user_id) -> dict:
    """
    Fetch last 5 transactions across all user accounts.
    Returns type, amount, and date for each transaction.
    """

    transaction_history = [
        {"type": "debit", "amount": 500, "date": "2025-07-17","remarks": "buying watch"},
        {"type": "debit", "amount": 500, "date": "2025-07-17","remarks": "buying watch"},
        {"type": "debit", "amount": 1000, "date": "2025-07-15","remarks": "electricity bill"},
        {"type": "credit", "amount": 32000, "date": "2025-07-14","remarks": "salary credited"},
        {"type": "debit", "amount": 200, "date": "2025-07-13","remarks": "buying grocery"},
        {"type": "debit", "amount": 1000, "date": "2025-07-15","remarks": "internet bill"},
        {"type": "credit", "amount": 32000, "date": "2025-07-14","remarks": "investmetn scheme"},
        {"type": "debit", "amount": 200, "date": "2025-07-13","remarks": "buying watch"}
    ]
    return transaction_history

@tool
def raise_dispute(user_id, transaction_date, transaction_amount):
    """
    Simulate raising a dispute for a transaction.
    Returns a confirmation message.
    """
    # In a real application, this would involve more complex logic and possibly an API call
    return {
        "status": "success",
        "message": f"Dispute raised for transaction on {transaction_date} of amount {transaction_amount}."
    }