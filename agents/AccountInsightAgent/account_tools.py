from langchain.tools import tool

@tool
def get_account_summary(user_id: str) -> dict:
    """
    Retrieve account balances and product summary for the user.
    Returns account types, balances, tenure, and activity level.
    """
    return {
        "user_id": user_id,
        "accounts": [
            {"type": "savings", "balance": 55000, "active": True, "tenure_months": 24},
            {"type": "current", "balance": 150000, "active": False, "tenure_months": 36}
        ]
    }