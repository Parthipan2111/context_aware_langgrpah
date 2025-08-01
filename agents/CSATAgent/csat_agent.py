from datetime import datetime
from typing import Any

from shared.MultiAgentState import MultiAgentState
from shared.parse_agent_response import parse_csat_response
from .prompt import CSAT_AGENT_PROMPT
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain


from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from graph.build_dynamic_graph import register_agent
from shared.constants import AGENT_NAME_DICT

current_agent = AGENT_NAME_DICT["CSAT"]
system_message = SystemMessagePromptTemplate.from_template(
    CSAT_AGENT_PROMPT
)

human_prompt = HumanMessagePromptTemplate.from_template("{history}")

# 3. Combine into a chat prompt template
prompt = ChatPromptTemplate.from_messages([system_message, human_prompt])

# 4. Load LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# 6. Initialize AgentExecutor
csat_agent = LLMChain(llm=llm,prompt=prompt)


@register_agent(current_agent)
def csat_scoring_node(state) -> MultiAgentState:
    """
    Node to compute and log CSAT for the current active_agent context.
    """

    session = state["session"]
    agent_context = session.intent
    history = session.history

    # --- Dummy scoring logic ---
    # Replace this with an LLM-based scoring or user feedback capture
    response_dict = csat_agent.invoke({"history": history})
    final_output = response_dict["text"]

    score,reason= parse_csat_response(final_output)


    # Ensure csat_scores exists in global_slots
    if "csat_scores" not in session.global_slots:
        session.global_slots["csat_scores"] = []

    # Append a new entry for this agent/context
    if score: 
        session.global_slots["csat_scores"].append({
            "context": agent_context or "general",
            "score": score,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        })

    # Optionally log for debugging
    print(f"[CSAT NODE] Logged score {score} for context {current_agent}")

    # Return the updated state
    return state
