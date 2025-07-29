import json

from requests import session
from shared.MultiAgentState import MultiAgentState


def safe_merge_agent_result(state: MultiAgentState, agent_name: str, agent_response: dict) -> MultiAgentState:
    """
    Merge the given agent's result into the agent_results field
    of the MultiAgentState without mutating the original state.
    """
    session = state["session"]
    # Make sure agent_results exists on the session
    if not hasattr(session, "agent_results"):
        session.agent_results = {}
    # Parse the agent response if it's a string
    if isinstance(agent_response, str):
        parsed_agent_response = parse_agent_results(agent_response)
    # Save back to session
    session.agent_results = parsed_agent_response

    # Return the same state (no need to modify top-level keys)
    return state

def parse_agent_results(raw: dict) -> dict:
    parsed_results = {}
    for agent, value in raw.items():
        if isinstance(value, str):
            try:
                parsed_results[agent] = json.loads(value)
            except json.JSONDecodeError:
                # Keep the raw string if it isn't valid JSON
                parsed_results[agent] = value
        else:
            parsed_results[agent] = value
    return parsed_results