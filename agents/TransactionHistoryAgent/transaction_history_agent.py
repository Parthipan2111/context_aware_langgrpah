from urllib import response
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

from langchain.agents import AgentExecutor, create_openai_functions_agent,Tool
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

from shared.parse_agent_response import parse_agent_response
from shared.session_model import AgentSlots
from shared.slot_utils import verify_slot
from .transaction_tools import get_recent_transactions
from graph.build_dynamic_graph import register_agent
from shared import MultiAgentState, state
from shared.merge_result import safe_merge_agent_result
from .prompt import TRANSACTION_AGENT_PROMPT
from shared.constants import AGENT_NAME_DICT

current_agent = AGENT_NAME_DICT["TRANSACTION_HISTORY"]
system_message = SystemMessagePromptTemplate.from_template(
    TRANSACTION_AGENT_PROMPT
)

tools = [
    Tool.from_function(name="get_recent_transactions",
                       description="Fetches the user's recent transactions.",
                       func=get_recent_transactions),
]

human_prompt = HumanMessagePromptTemplate.from_template("{user_id},{user_input},{slots}")

# 3. Combine into a chat prompt template
prompt = ChatPromptTemplate.from_messages([system_message, human_prompt,("ai", "{agent_scratchpad}")])

# 4. Load LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# llm = ChatGroq(
#         model="llama-3.1-8b-instant",  # or "mixtral-8x7b-32768", etc.
#         temperature=0.7,
#     )

# llm = ChatGroq(model="llama3-8b-8192", temperature=0.7)
# 5. Build agent
agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)

# 6. Initialize AgentExecutor
transaction_history_agent = AgentExecutor(agent=agent, tools=tools, verbose=True)


@register_agent(current_agent)
def transaction_history(state: dict) -> MultiAgentState:
    # 1. Extract user input and user_id from the state

    user_input = state["user_input"]
    user_id = state["session"].user_id
    slots = state.get("agent_state", {}).get(current_agent, {}).get("slots", {})

    response_dict = transaction_history_agent.invoke({"user_id": user_id, "user_input": user_input, "slots": slots})
    final_output = response_dict["output"]
    slot_parsed,agent_response,reasoning = parse_agent_response(final_output)
    session = state["session"]
# ---- Update slots in session.agent_state ----
    if slot_parsed:
        verify_slot(slot_parsed,current_agent,session)
    if reasoning:
        session.reasoning[current_agent] = reasoning

    session.add_message("assistant", final_output)
    return safe_merge_agent_result(state, current_agent, agent_response)
