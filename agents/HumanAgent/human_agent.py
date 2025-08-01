from graph.build_dynamic_graph import register_agent
from shared.MultiAgentState import MultiAgentState
from shared.merge_result import safe_merge_agent_result
from shared.session_model import AgentSlots, SessionState,PendingAgent
from shared.constants import AGENT_NAME_DICT

current_agent = AGENT_NAME_DICT["HUMAN"]
@register_agent(current_agent)
def human_agent_node(state) -> MultiAgentState:
    """ Initialize the state for human agent.
    """
    session: SessionState = state["session"]
    user_input = state["user_input"]
    agent_response: str = (
        f"Hi , Now you are talking with an Human Agent, "
        f"I saw ur {user_input}. I will try to see how can i can resolve your issue, "
        f"Thanks for the patience!"
    )

    session.add_message("human", agent_response)

    session.reasoning[current_agent] = "As per the query, the AI agent cannot resolve the issue, so I am stepping in to help the user"

    return safe_merge_agent_result(state, current_agent, agent_response)

    
    # Return the updated MultiAgentState
    return state