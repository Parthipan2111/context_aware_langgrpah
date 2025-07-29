from urllib import response
from langchain.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

from langchain.agents import AgentExecutor, create_openai_functions_agent,Tool
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

from shared.session_model import AgentSlots
from .transaction_tools import get_recent_transactions
from graph.build_dynamic_graph import register_agent
from shared import MultiAgentState, state
from shared.merge_result import safe_merge_agent_result
from .prompt import TRANSACTION_AGENT_PROMPT
import json
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

current_agent = "transaction_history"

@register_agent(current_agent)
def transaction_history(state: dict) -> MultiAgentState:
    # 1. Extract user input and user_id from the state

    user_input = state["user_input"]
    user_id = state["session"].user_id
    slots = state.get("agent_state", {}).get(current_agent, {}).get("slots", {})

    # response = account_insight_agent.run(user_input)
    final_output = """
    {
    "slots": {
        "no_of_days": "5"
    },
    "agent_response": [
        "Here is the analysis of your transaction history for the past 5 days:",
        "- Total number of transactions: 8",
        "- Debit transactions: 4, totaling 3,700",
        "- Credit transactions: 4, totaling 79,000",
        "- Date range of transactions: From 2025-07-13 to 2025-07-17"
    ]
    }
    """
    # response_dict = transaction_history_agent.invoke({"user_id": session.user_id, "user_input": user_input, "slots": slots})
    # final_output = response_dict["output"]
    try:
        parsed = json.loads(final_output)
        slot_parsed = parsed.get("slots", {})
        agent_response = parsed.get("agent_response", [])
        print("Slots:", slot_parsed)
        print("Response:", agent_response)
    except json.JSONDecodeError:
    # If JSON decoding fails, fallback to using the raw output
        slot_parsed = {}
        agent_response = [final_output]
        print("Model did not return valid JSON:", final_output)

    session = state["session"]

# ---- Update slots in session.agent_state ----
    if slot_parsed:
        # Ensure the agent state exists
        if current_agent not in session.agent_state:
            session.agent_state[current_agent] = AgentSlots()

        for key, value in slot_parsed.items():
            session.agent_state[current_agent].slots[key] = value

    # ---- Add message to history ----
    session.add_message("assistant", final_output)

    # ---- Check if all slots for this agent are filled ----
    if slot_parsed:
        slots_dict = session.agent_state[current_agent].slots
        all_filled = all(v is not None and v != "" for v in slots_dict.values())

        if all_filled:
            # Remove current agent from pending_agents
            session.pending_agents = [
                a for a in session.pending_agents if a["name"] != current_agent
            ]

            # If no pending agents remain, clear active_agent
            if not session.pending_agents:
                session.active_agent = None
    return safe_merge_agent_result(state, "transaction_history_agent", agent_response)
