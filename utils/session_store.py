# app/session_store.py
import json
from typing import Optional
from mongo_db.mongo_client import mongo_sessions
from redis_store.redis_client import REDIS_CLIENT as redis_client
from shared.MultiAgentState import MultiAgentState
from shared.session_model import SessionState

def load_session(user_id: str, session_id: str = None) -> dict:
    data = redis_client.get(session_id)
    if data:
        return json.loads(data)
    # 2. Try Mongo
    query = {"session_id": session_id}
    if user_id:
        # Optionally ensure we match the correct user as well
        query["user_id"] = user_id

    doc = mongo_sessions.find_one(query)
    return doc["state"] if doc else None

def save_session(session_state: dict, ttl: int = 3600):
     # Always include both session_id and user_id in the persisted state

    session_id = session_state["session_id"]
    user_id = session_state["user_id"]
    redis_client.set(session_id, json.dumps(session_state), ex=ttl)
    mongo_sessions.update_one(
        {"session_id": session_id},
        {"$set": {"state": session_state,"user_id":user_id}},
        upsert=True
    )
