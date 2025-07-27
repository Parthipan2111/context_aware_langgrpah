from langchain.agents import Tool, AgentExecutor, AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.agents import AgentExecutor, create_openai_functions_agent,Tool
from graph.build_dynamic_graph import register_agent
from shared.merge_result import safe_merge_agent_result
from .prompt import CARD_MANAGEMENT_PROMPT
from agents.CardManagementAgent.card_tools import get_user_cards, block_card, request_new_card, get_card_limit

llm = ChatOpenAI(model="gpt-4", temperature=0)

tools = [
    Tool.from_function(name="get_user_cards", func=get_user_cards,description="Fetch active credit and debit cards for the user."),
    Tool.from_function(name="block_card", func=block_card, description="Block a specific card."),
    Tool.from_function(name="request_new_card", func=request_new_card, description="Request a new card."),
    Tool.from_function(name="get_card_limit", func=get_card_limit, description="Get the limit for a specific card.")
]

# 1. Define the system message (your custom prompt)
system_message = SystemMessagePromptTemplate.from_template(
CARD_MANAGEMENT_PROMPT
)

human_prompt = HumanMessagePromptTemplate.from_template("{user_input}, {slots}")

# 3. Combine into a chat prompt template
prompt = ChatPromptTemplate.from_messages([system_message, human_prompt,("ai", "{agent_scratchpad}")])

llm = ChatOpenAI(model="gpt-4o", temperature=0)

# 5. Build agent
agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)

# 6. Initialize AgentExecutor
card_management_agent = AgentExecutor(agent=agent, tools=tools, verbose=True)

@register_agent("card_management_agent")
def card_management_node(state):
    """ Node for card management in the LangGraph workflow.
    This node handles card-related tasks such as blocking a card, requesting a new card, or checking card limits.
    """
    user_input = state["user_input"]
    session = state["session"]
    # fetch the slots required from the state
    slots = state.get("agent_state", {}).get("card_management", {}).get("slots", {})
    response = card_management_agent.run("{user_input}, {slots}")
    session = state["session"]
    session.history.append({"role": "assistant", "content": response})
    return safe_merge_agent_result(state, "card_management_agent", {"card_output": response})
