# api/models.py
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    text: str = Field(..., description="User message text")
    user_id: str = Field(..., description="User ID")
    session_id: str = Field(..., description="Session ID for tracking conversation state")
    channel: str = Field(..., description="Channel identifier (e.g., 'web', 'mobile')")

class ChatResponse(BaseModel):
    response: str = Field(..., description="Chatbot response text")
    user_id: str = Field(..., description="User ID")
    context: dict = Field(..., description="Contextual information for the response")
