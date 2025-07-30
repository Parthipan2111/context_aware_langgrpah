from urllib import response
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

from langchain.agents import AgentExecutor, create_openai_functions_agent,Tool
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from agents.AccountInsightAgent.account_tools import get_account_summary
from graph.build_dynamic_graph import register_agent
from shared import MultiAgentState
from shared.merge_result import safe_merge_agent_result
from shared.parse_agent_response import parse_agent_response
from shared.slot_utils import verify_slot
from .prompt import ACCOUNT_INSIGHT_PROMPT

system_message = SystemMessagePromptTemplate.from_template(
    ACCOUNT_INSIGHT_PROMPT
)

tools = [
    Tool.from_function(name="get_account_summary",
                       description="Fetches the user's account summary including balances, credit limits, and usage patterns.",
                       func=get_account_summary)
]

human_prompt = HumanMessagePromptTemplate.from_template("{user_id}")

# 3. Combine into a chat prompt template
prompt = ChatPromptTemplate.from_messages([system_message, human_prompt,("ai", "{agent_scratchpad}")])

# 4. Load LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# llm = ChatOpenAI(
#     model="openhermes",
#     base_url="http://localhost:11434/v1",  # Ollama API endpoint
# )

# llm = ChatGroq(model="llama3-8b-8192", temperature=0.7)
# 5. Build agent
agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)

# 6. Initialize AgentExecutor
account_insight_agent = AgentExecutor(agent=agent, tools=tools, verbose=True)

current_agent = "account_insight_agent"

@register_agent("get_account_insight")
def account_insight_node(state) -> MultiAgentState:
    # 1. Extract user input and user_id from the state
    user_input = state["user_input"]
    user_id = state["session"].user_id

    response_dict = account_insight_agent.invoke({"user_id": user_id, "user_input": user_input })
    final_output = response_dict["output"]
    session = state["session"]
    session.add_message("assistant", final_output)
    session.pending_agents = [
            a for a in session.pending_agents if a.name != current_agent
        ]
    if not session.pending_agents:
            session.active_agent = None
    return safe_merge_agent_result(state, current_agent, final_output)
