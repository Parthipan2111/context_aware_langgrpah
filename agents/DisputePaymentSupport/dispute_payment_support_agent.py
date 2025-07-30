from urllib import response
from langchain.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

from langchain.agents import AgentExecutor, create_openai_functions_agent,Tool
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

from shared.slot_utils import verify_slot
from .tools import get_recent_transactions
from graph.build_dynamic_graph import register_agent
from shared import MultiAgentState, parse_agent_response, state
from shared.merge_result import safe_merge_agent_result
from .prompt import DISPUTE_PAYMENT_SUPPORT_AGENT_PROMPT
from .tools import raise_dispute
from shared.parse_agent_response import parse_agent_response
import json
system_message = SystemMessagePromptTemplate.from_template(
    DISPUTE_PAYMENT_SUPPORT_AGENT_PROMPT
)

tools = [
    Tool.from_function(name="get_recent_transactions",
                       description="Fetches the user's recent transactions.",
                       func=get_recent_transactions),
    Tool.from_function(name="raise_dispute",
                       description="Raises a dispute for the specified transaction.",
                       func=raise_dispute)
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
dispute_payment_support_agent = AgentExecutor(agent=agent, tools=tools, verbose=True)

current_agent = "dispute_payment_support"

@register_agent(current_agent)
def dispute_payment_support(state: dict) -> MultiAgentState:
    # 1. Extract user input and user_id from the state
    user_input = state["user_input"]
    user_id = state["session"].user_id
    session = state["session"]

    slots = session.get_agent_slots(current_agent)

    response_dict = dispute_payment_support_agent.invoke({"user_id": user_id, "user_input": user_input, "slots": slots})
    final_output = response_dict["output"]
    # final_output = """
    #         {
    #         "slots": {
    #             "transaction_date": "",
    #             "transaction_amount": "50",
    #             "user_final_confirmation": ""
    #         },
    #         "agent_response": [
    #             "I understand you want to raise a dispute for a transaction of 50 dollars. Could you please provide the exact date of the transaction last week?"
    #         ]
    #         }
    #     """
    slot_parsed,agent_response = parse_agent_response(final_output)
# ---- Update slots in session.agent_state ----
    if slot_parsed:
        verify_slot(slot_parsed,current_agent,session)
    session.add_message("assistant", final_output)

    return safe_merge_agent_result(state, current_agent, agent_response)
