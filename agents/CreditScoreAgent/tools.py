from langchain.tools import tool

@tool
def get_credit_data(user_id: str) -> dict:
    """
    Fetch the user's credit data from a bureau.
    Includes score, open loans, defaults, utilization, late payments.
    """
    return {
        "user_id": user_id,
        "credit_score": 660,
        "defaults_last_year": 1,
        "open_loans": 3,
        "credit_utilization": 72,  # %
        "late_payments": 2
    }

@tool
def get_user_profile(user_id: str) -> dict:
    """
    Retrieve the user's financial profile.
    Includes name, income bracket, employment type, and existing products.
    """
    return {
        "name": "Amit Verma",
        "income_bracket": "5-8 LPA",
        "employment": "Salaried",
        "existing_products": ["credit_card", "personal_loan"]
    }
