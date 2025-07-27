from sqlalchemy import cast
from shared.MultiAgentState import MultiAgentState
import uuid
from shared.session_model import SessionState
from shared.session_model import HistoryItem

def init_new_multi_agent_state(user_id: str, session_id: str, user_input: str) -> MultiAgentState:
    session_state = SessionState(
        session_id=session_id,
        user_id=user_id,  # Set to None for new sessions; can be updated later
        active_agent=None,
        history=[HistoryItem(role="user", content=user_input)],
        global_slots={},
        agent_state={},
        pending_agents=[],
        intent=[],
        input=user_input,
        similar_context=None,
        workflow_complete=False  # Initialize as incomplete
    )
    return {
        "session": session_state,
        "user_input": user_input,
        "output": ""
    }
