from langchain.agents import Tool, initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from shared.MultiAgentState import MultiAgentState
from tools import get_credit_data, get_user_profile
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


@register_agent("credit_score_agent")
def credit_score_node(state) -> MultiAgentState:
    """
    Node for credit score analysis in the LangGraph workflow.
    This node fetches credit data, analyzes the score, and provides recommendations.
    """
    user_id = state["user_id"]
    
    # Run the agent with the user input
    response = credit_score_agent.run(user_id)
    session = state["session"]
    session.history.append({"role": "assistant", "content": response})
    # Return the response as a structured output
    return safe_merge_agent_result(state, "credit_score_agent", {"credit_score": response})