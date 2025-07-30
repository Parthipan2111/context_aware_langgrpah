from graph.build_dynamic_graph import register_agent
from shared.MultiAgentState import MultiAgentState
from shared.session_model import AgentSlots, SessionState,PendingAgent


@register_agent("router_node")
def update_state_with_agents(state) -> MultiAgentState:
    """ Initialize the state for intent recognition.
    """
    session: SessionState = state["session"]
    intents = session.intent

    for intent in intents:
        # Initialize default slots depending on intent
        if intent not in session.agent_state:
            if intent == "dispute_payment_support":
                default_slots = {
                    "transaction_date": None,
                    "transaction_amount": None,
                    "user_final_confirmation": None,
                }
            elif intent == "card_management":
                default_slots = {
                    "last_four_digits_card_number": None,
                    "reason": None,
                    "user_final_confirmation": None,
                }
            elif intent == "transaction_history":
                default_slots = {"no_of_days": None}
            else:
                default_slots = {}

            # Use AgentSlots model
            session.agent_state[intent] = AgentSlots(slots=default_slots)

    # Prepare pending_agents as a list of dicts
    session.pending_agents = [PendingAgent(name=intent, mode="parallel") for intent in intents]

    # If single intent, set active_agent
    session.active_agent = intents[0] if len(intents) == 1 else None
    
    # Return the updated MultiAgentState
    return state