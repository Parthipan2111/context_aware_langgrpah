# api/main.py
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware


from api.chat_model import ChatRequest
from api.exception_handler import validation_exception_handler, langgraph_exception_handler, LangGraphProcessingError
from langgraph_app.service import run_langgraph
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from shared.auth import verify_token
from datetime import timedelta

app = FastAPI()

# Optional CORS setup for frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(LangGraphProcessingError, langgraph_exception_handler)

@app.post("/chat")
def chat(request: ChatRequest, 
        #  user=Depends(verify_token(required_groups=["agent_group"]))
        ):
    """
    Sync endpoint for channel adapters
    """
    try:
        response = run_langgraph(request)
        return {"response": response}
    except Exception as e:
        raise LangGraphProcessingError(f"Failed to process message: {str(e)}")

# @app.post("/chat/stream")
# async def chat_stream(request: ChatRequest):
#     """
#     Streaming endpoint
#     """
#     try:
#         async def event_generator():
#             async for chunk in run_langgraph_stream(request.text, request.session_id):
#                 yield chunk
#         return StreamingResponse(event_generator(), media_type="text/plain")
#     except Exception as e:
#         raise LangGraphProcessingError(f"Failed to process stream: {str(e)}")

   
