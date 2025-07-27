from pydantic import BaseModel
from typing import List, Optional

class SessionSummary(BaseModel):
    topic: str
    outcome: str

class ContextData(BaseModel):
    device: str
    location: str
    language: str
    last_sessions: List[SessionSummary]

class EnrichedResponse(BaseModel):
    original_input: str
    context: ContextData
