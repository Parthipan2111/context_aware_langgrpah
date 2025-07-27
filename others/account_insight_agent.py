from langchain.agents import Tool, initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from shared.state import GraphState
from ..agents.AccountInsightAgent.account_tools import get_account_summary, get_recent_transactions
import os

tools = [
    Tool.from_function(name="get_account_summary",description="Fetches the user's account summary including balances, credit limits, and usage patterns.",func=get_account_summary),
    Tool.from_function(name="get_recent_transactions", description="Fetches the user's recent transactions.", func=get_recent_transactions)
]

system_prompt = """
You are AccountInsightAgent.

Provided the account type and user input, you will analyze the user's account health and provide recommendations.

Responsibilities:
1. Fetch account summary based on the account type and recent transactions using the tools.
2. Output a structured JSON:
{
  "account_health": <summary>,
  "recommendations": [<string>, <string>]
}
Only return JSON. Be insightful and user-friendly.
"""

llm = ChatOpenAI(model="gpt-4o", temperature=0)

account_insight_agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True
)


def account_insight_node(state) -> GraphState:
    user_input = state["input"]
    response = account_insight_agent.run(user_input)
    final_output = response

    state["messages"].append({
        "role": "assistant",
        "content": response
    })
    return state
