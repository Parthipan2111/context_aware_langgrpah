from typing import Dict
from typing import TypedDict, Any
from shared.session_model import SessionState

class MultiAgentState(TypedDict):
    session: SessionState
    user_input: str
    output: str
