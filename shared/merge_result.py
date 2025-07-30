import json

from requests import session
from shared.MultiAgentState import MultiAgentState


def safe_merge_agent_result(state: MultiAgentState, agent_name: str, agent_response: list | str) -> MultiAgentState:
    """
    Stores agent_response (list or string) under session.agent_results[agent_name].
    Expects agent_response to already be a list from the agent, not a dictionary.
    """
    session = state["session"]

    # Ensure agent_results exists
    if not hasattr(session, "agent_results"):
        session.agent_results = {}

    # Normalize to list
    if isinstance(agent_response, str):
        responses = [agent_response]
    else:
        responses = agent_response

    # Save/merge
    session.agent_results[agent_name] = responses
    return state
