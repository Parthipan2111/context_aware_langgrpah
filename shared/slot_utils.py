from shared.session_model import AgentSlots, SessionState


def verify_slot(slot_parsed, current_agent:str ,session: SessionState):
        # Ensure the agent state exists
    if current_agent not in session.agent_state:
        session.agent_state[current_agent] = AgentSlots()

    for key, value in slot_parsed.items():
        session.agent_state[current_agent].slots[key] = value

    # ---- Check if all slots for this agent are filled ----
    slots_dict = session.agent_state[current_agent].slots
    all_filled = all(v is not None and v != "" for v in slots_dict.values())
    if all_filled:
            # Remove current agent from pending_agents
        session.pending_agents = [
            a for a in session.pending_agents if a.name != current_agent
        ]
        # If no pending agents remain, clear active_agent
        if not session.pending_agents:
            session.active_agent = None