
from graph.build_dynamic_graph import register_agent
from shared import MultiAgentState
from shared.merge_result import safe_merge_agent_result

@register_agent("transaction_history_agent")
def get_recent_transactions(state) -> MultiAgentState:
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
    session = state["session"]
    session.history.append([
        {"role": "assistant", "content": f"Transaction {i + 1}: {tx['type']} of ${tx['amount']} on {tx['date']}"}
        for i, tx in enumerate(transaction_history[:5])
    ])
    # Update the state with the transaction history
    response = "\n".join(
        f"Transaction {i + 1}: {tx['type']} of ${tx['amount']} on {tx['date']}"
        for i, tx in enumerate(transaction_history[:5])
    )
    return safe_merge_agent_result(state, "transaction_history_agent", {"transaction_history": response})
