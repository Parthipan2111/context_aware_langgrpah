# api/models.py
from typing import List, Optional
from pydantic import BaseModel, Field

from shared.session_model import HistoryItem

class ChatRequest(BaseModel):
    text: str = Field(..., description="User message text")
    user_id: str = Field(..., description="User ID")
    session_id: str = Field(..., description="Session ID for tracking conversation state")
    channel: str = Field(..., description="Channel identifier (e.g., 'web', 'mobile')")

class ChatResponse(BaseModel):
    agent_response: str = Field(..., description="Chatbot response text")
    user_id: str = Field(..., description="User ID")
    history: List[HistoryItem] = Field(default_factory=list)
    scratchpad: Optional[str] = Field(None, description="Internal reasoning trace (agent_scratchpad)")
