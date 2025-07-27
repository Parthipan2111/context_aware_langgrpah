# api/exceptions.py
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi import status
from fastapi.exception_handlers import RequestValidationError
from fastapi.exceptions import RequestValidationError

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Invalid input",
            "details": exc.errors()
        },
    )

class LangGraphProcessingError(Exception):
    def __init__(self, message: str):
        self.message = message

async def langgraph_exception_handler(request: Request, exc: LangGraphProcessingError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": exc.message},
    )
