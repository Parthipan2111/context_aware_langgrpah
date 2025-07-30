from langchain.agents import Tool
from langchain_openai import ChatOpenAI
from shared.MultiAgentState import MultiAgentState
from .tools import get_credit_data, get_user_profile
from graph.build_dynamic_graph import register_agent
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.agents import AgentExecutor, create_openai_functions_agent,Tool
from shared.merge_result import safe_merge_agent_result
from .prompt import CREDIT_SCORE_PROMPT


# Define tools
tools = [
    Tool.from_function(name="get_credit_data",
                       func=get_credit_data,
                       description="Fetches the user's credit data from a bureau."),
    Tool.from_function(name="get_user_profile",
                       func=get_user_profile,
                       description="Fetches the user's profile information.")
]

# 1. Define the system message (your custom prompt)
system_message = SystemMessagePromptTemplate.from_template(
CREDIT_SCORE_PROMPT
)

human_prompt = HumanMessagePromptTemplate.from_template("{user_id}")

# 3. Combine into a chat prompt template
prompt = ChatPromptTemplate.from_messages([system_message, human_prompt,("ai", "{agent_scratchpad}")])

llm = ChatOpenAI(model="gpt-4o", temperature=0)

# 5. Build agent
agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)

# 6. Initialize AgentExecutor
credit_score_agent = AgentExecutor(agent=agent, tools=tools, verbose=True)

current_agent ="credit_score"

@register_agent("credit_score")
def credit_score_node(state) -> MultiAgentState:
    """
    Node for credit score analysis in the LangGraph workflow.
    This node fetches credit data, analyzes the score, and provides recommendations.
    """
    user_id = state["session"].user_id    
    # Run the agent with the user input
    response = credit_score_agent.invoke({"user_id":user_id})
    final_output = response["output"]
    session = state["session"]
    session.add_message("assistant", final_output)
    session.pending_agents = [
            a for a in session.pending_agents if a.name != current_agent
        ]
    if not session.pending_agents:
            session.active_agent = None
    # Return the response as a structured output
    return safe_merge_agent_result(state, current_agent, final_output)