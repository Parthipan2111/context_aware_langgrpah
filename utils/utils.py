from shared import MultiAgentState


def start_or_resume(state: MultiAgentState) -> MultiAgentState:
    """
    Entry point for deciding whether to resume an incomplete agent flow
    or start a new query. Now checks pending_agents and active_agent
    inside the SessionState (state["session"]).
    """
    session = state["session"]  # SessionState object
    user_input = state["user_input"]

    # Check if there are any unfinished agents
    if getattr(session, "pending_agents", []):
        # Resume workflow for pending agents
        session.add_message("system", f"Resuming pending agents: {[p.name if hasattr(p,'name') else p for p in session.pending_agents]}")
        return state

    # Check if an active agent is set (single-agent scenario)
    if getattr(session, "active_agent", None):
        session.add_message("system",  f"Continuing with active agent: {session.active_agent}")
        return state

    # Otherwise, no pending work: proceed with context enrichment + intent recognition
    session.add_message("system",  f"Starting new flow for input: {user_input}")
    session.agent_state.clear()
    session.pending_agents.clear()
    session.agent_results.clear()
    session.active_agent = None
    return state

