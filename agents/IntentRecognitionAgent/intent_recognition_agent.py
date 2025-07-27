# agents/intent_recognition/node.py

from typing import TypedDict
from langchain.prompts import PromptTemplate

from graph.build_dynamic_graph import register_agent
from shared import MultiAgentState
from .prompt import INTENT_PROMPT_TEMPLATE
from langchain_groq import ChatGroq

# Define or import GraphState
from typing import Dict, Any


@register_agent("intent_agent")
def intent_recognition_node(state) -> MultiAgentState:
    """
    Node for intent recognition in the LangGraph workflow.
    This node classifies the user's input into one or more intents.
    """
    user_input = state["user_input"]
    
    # Classify the intent using the classify_intent function
    intent_text = classify_intent(user_input)
    
    # Split the intents by comma and strip whitespace
    intents = [s.strip() for s in intent_text.split(",") if s.strip()]
    
    # Update the state with recognized intents
    return update_state_with_intent(state, intents)


def classify_intent(user_input: str) -> str:
    llm = ChatGroq(
        model="llama3-8b-8192",  # or "mixtral-8x7b-32768", etc.
        temperature=0.7,
    )
    prompt = PromptTemplate.from_template(INTENT_PROMPT_TEMPLATE)
    chain = prompt | llm
    intent = chain.invoke({"message": user_input}).content.strip()

    return intent

def update_state_with_intent(state: MultiAgentState, intents: list[str]) -> MultiAgentState:
    """ Initialize the state for intent recognition.
    """
    # 3. Initialize agent_state for all detected agents
    state.setdefault("agent_state", {})
    for intent in intents:
        if intent not in state["agent_state"]:
            if intent == "dispute_payment_support":
                default_slots = {"transaction_date": None, "amount": None,"user_final_confirmation": None}
            elif intent == "service_ticket_enquiry":
                default_slots = {"service_ticket_id": None}
            elif intent == "card_management":
                default_slots = {"last_four_digits_card_number": None, "reason": None,"user_final_confirmation": None}
            elif intent == "get_account_info":
                default_slots = {"account_type": None}
            elif intent == "transaction_history":
                default_slots = {"period_in_days": None}
            else:
                default_slots = {}
            state["agent_state"][intent] = {"slots": default_slots}

    # 4. Prepare pending_agents list (all parallel)
    state["pending_agents"] = [{"name": intent, "mode": "parallel"} for intent in intents]

    # If only one agent, we can set active_agent; otherwise, leave None
    state["active_agent"] = intents[0] if len(intents) == 1 else None
    state["intent"] = intents if len(intents) > 1 else intents[0]
    session = state["session"]
    session.history.append(
            {"role": "system", "content": f"Found the intent for query as: {intents}"}
        )
    return state
