"""
Chat endpoint for our-ai-demo V0.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.core.orchestrator import create_orchestrator, Orchestrator
from app.core.ai_provider import get_ai_provider
from app.core.simulator import Simulator
import logging


def sanitize_error_message(exc: Exception) -> str:
    """
    Sanitize exception messages for client responses.
    Returns a user-friendly error message while logging the full details internally.
    """
    # Log the full exception details for debugging
    logging.getLogger(__name__).exception("Internal error occurred")

    # Return user-friendly messages for common error types
    if isinstance(exc, ValueError):
        return "Invalid request data provided."
    elif isinstance(exc, PermissionError):
        return "Insufficient permissions to perform this action."
    elif exc and ("database" in str(exc).lower() or "connection" in str(exc).lower()):
        return "Unable to connect to database. Please try again later."
    elif exc and "timeout" in str(exc).lower():
        return "Request timed out. Please try again."
    else:
        # For all other exceptions, return a generic message
        return "An internal error occurred. Please try again or contact support."

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


# We'll create a singleton simulator and orchestrator for simplicity
# In a production application, you might want to manage these per request or use dependency injection
_simulator = None
_ai_provider = None
_orchestrator = None


def get_simulator() -> Simulator:
    global _simulator
    if _simulator is None:
        _simulator = Simulator()
    return _simulator


def get_ai_provider_instance():
    global _ai_provider
    if _ai_provider is None:
        _ai_provider = get_ai_provider()
    return _ai_provider


def get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        ai_provider = get_ai_provider_instance()
        simulator = get_simulator()
        _orchestrator = create_orchestrator(ai_provider, simulator)
    return _orchestrator


@router.post("/chat")
async def chat_endpoint(
    request: ChatRequest,
    orchestrator: Orchestrator = Depends(get_orchestrator),
):
    """Process a user message and return a response."""
    try:
        result = await orchestrator.process_message(request.message)
        return {
            "message": result.get("message", "I'm sorry, I couldn't process your request."),
            "intent": result.get("intent"),
            "tool_executions": result.get("tool_executions"),
            "verification_results": result.get("verification_results"),
        }
    except Exception as e:
        # Return sanitized error message to client
        error_message = sanitize_error_message(e)
        raise HTTPException(status_code=500, detail=error_message)


# We need to import logger
import logging
logger = logging.getLogger(__name__)