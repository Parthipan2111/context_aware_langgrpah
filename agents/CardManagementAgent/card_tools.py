from langchain.tools import tool

@tool
def get_user_cards(user_id: str) -> list:
    """Fetch active credit and debit cards for the user."""
    return [
        {"card_id": "C123", "type": "credit", "last4": "1234"},
        {"card_id": "C456", "type": "debit", "last4": "5678"},
    ]

@tool
def block_card(card_id: str) -> str:
    """Block a card based on card ID."""
    return f"Card {card_id} has been blocked."

@tool
def request_new_card(card_type: str) -> str:
    """Request a new card of specified type."""
    return f"A new {card_type} card will be issued."

@tool
def get_card_limit(card_id: str) -> dict:
    """Get the credit limit and usage of a card."""
    return {"limit": 100000, "used": 45000}
