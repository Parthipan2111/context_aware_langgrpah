from shared.session_model import SessionState
from mongo_db.mongo_client import mongo_trace_log
from datetime import datetime


def log_agent_steps(session: SessionState, agent: str, input_text: str, output: str, explanation: str):
    trace = {
        "timestamp": datetime.utcnow().isoformat(),
        "agent": agent,
        "input": input_text,
        "output": output,
        "explanation": explanation
    }
    mongo_trace_log.insert_one({**trace, "session_id": session.session_id, "user_id": session.user_id})
