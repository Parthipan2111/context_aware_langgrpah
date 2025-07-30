from langchain.agents import Tool, AgentExecutor, AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.agents import AgentExecutor, create_openai_functions_agent,Tool
from graph.build_dynamic_graph import register_agent
from shared.merge_result import safe_merge_agent_result
from shared.parse_agent_response import parse_agent_response
from shared.slot_utils import verify_slot
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

current_agent= "card_management"

@register_agent("card_management")
def card_management_node(state):
    """ Node for card management in the LangGraph workflow.
    This node handles card-related tasks such as blocking a card, requesting a new card, or checking card limits.
    """
    user_input = state["user_input"]
    user_id = state["session"].user_id
    session = state["session"]

    slots = session.get_agent_slots(current_agent)

    response_dict = card_management_agent.invoke({"user_id": user_id, "user_input": user_input, "slots": slots})
    final_output = response_dict["output"]

    slot_parsed,agent_response = parse_agent_response(final_output)
# ---- Update slots in session.agent_state ----
    if slot_parsed:
        verify_slot(slot_parsed,current_agent,session)
    session.add_message("assistant", final_output)

    return safe_merge_agent_result(state, current_agent, agent_response)

