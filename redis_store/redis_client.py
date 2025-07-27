# langgraph_app/state_store.py
import json
import redis

REDIS_CLIENT = redis.Redis(host="localhost", port=6379, decode_responses=True)

SESSION_PREFIX = "session:"

def get_session_state(session_id: str) -> dict:
    data = REDIS_CLIENT.get(SESSION_PREFIX + session_id)
    return json.loads(data) if data else {}

def save_session_state(session_id: str, state: dict):
    REDIS_CLIENT.setex(SESSION_PREFIX + session_id, 3600, json.dumps(state))  # expires in 1h
    
def delete_session_state(session_id: str):
    REDIS_CLIENT.delete(SESSION_PREFIX + session_id)