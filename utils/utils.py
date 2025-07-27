from shared import MultiAgentState


def get_incomplete_agent_plan(state: MultiAgentState) -> list[dict]:
    """
    Returns a filtered list of agent dicts (name, mode) for agents
    that have incomplete slot data, preserving their original modes.
    """
    pending_agents = state.get("pending_agents", [])
    agent_state = state.get("agent_state", {})

    def is_incomplete(agent_name):
        slots = agent_state.get(agent_name, {}).get("slots", {})
        return any(v is None for v in slots.values())

    # Preserve the mode from the original plan
    return [agent for agent in pending_agents if is_incomplete(agent["name"])]
