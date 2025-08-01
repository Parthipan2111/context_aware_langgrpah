from urllib import response
from langchain.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain.chains import LLMChain


from langchain.agents import AgentExecutor, create_openai_functions_agent,Tool
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

from shared.slot_utils import verify_slot
from graph.build_dynamic_graph import register_agent
from shared import MultiAgentState, parse_agent_response, state
from shared.merge_result import safe_merge_agent_result
from .prompt_intent import INTENT_PROMPT_TEMPLATE
from shared.parse_agent_response import parse_agent_response
import json
from shared.constants import AGENT_NAME_DICT

current_agent = AGENT_NAME_DICT["INTENT_AGENT"]
system_message = SystemMessagePromptTemplate.from_template(
    INTENT_PROMPT_TEMPLATE
)

human_prompt = HumanMessagePromptTemplate.from_template("{user_input}")

#  Combine into a chat prompt template
prompt = ChatPromptTemplate.from_messages([system_message, human_prompt])

#  Load LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# Initialize AgentExecutor
intent_agent = LLMChain(llm=llm,prompt=prompt)


@register_agent(current_agent)
def intent_agent_node(state: dict) -> MultiAgentState:
    # 1. Extract user input and user_id from the state
    user_input = state["user_input"]
    session = state["session"]

    response_dict = intent_agent.invoke({"user_input": user_input})
    final_output = response_dict["text"]
    
    slot_parsed,agent_response,reasoning = parse_agent_response(final_output)
# ---- Update slots in session.agent_state ----
    if reasoning:
        session.reasoning[current_agent] = reasoning
    session.add_message("assistant", final_output)
    session.intent = agent_response

    return state
