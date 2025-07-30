# agents/intent_recognition/node.py

from typing import TypedDict
from langchain.prompts import PromptTemplate

from graph.build_dynamic_graph import register_agent
from shared import MultiAgentState
from shared.session_model import AgentSlots, SessionState
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
    session: SessionState = state["session"]
    
    # Classify the intent using the classify_intent function
    intent_text = classify_intent(user_input)
    
    # Split the intents by comma and strip whitespace
    intents = [s.strip() for s in intent_text.split(",") if s.strip()]
    session.intent = intents  

     # Log in history
    session.add_message(
        role="system",
        content=f"Found the intent for query as: {intents}",
    )  
    
    # Update the state with recognized intents
    return state


def classify_intent(user_input: str) -> str:
    llm = ChatGroq(
        model="llama3-8b-8192",  # or "mixtral-8x7b-32768", etc.
        temperature=0.7,
    )
    prompt = PromptTemplate.from_template(INTENT_PROMPT_TEMPLATE)
    chain = prompt | llm
    intent = chain.invoke({"message": user_input}).content.strip()

    return intent
