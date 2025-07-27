from langchain.tools import tool

@tool
def get_user_metadata(user_id: str) -> dict:
    """
    Fetch user metadata like device, location, and preferred language.
    Useful for routing, personalization, and compliance.
    """
    return {
        "device": "Android",
        "location": "Chennai",
        "language": "en-IN"
    }

@tool
def get_session_history(user_id: str) -> list:
    """
    Retrieve last 3 interaction summaries with the user.
    Returns topic and outcome of each session.
    """
    return [
        {"topic": "Credit Card Limit", "outcome": "Limit increased"},
        {"topic": "FD closure", "outcome": "Closed and payout initiated"},
        {"topic": "Account statement", "outcome": "PDF emailed"}
    ]
