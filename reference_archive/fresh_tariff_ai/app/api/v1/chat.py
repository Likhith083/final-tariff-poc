"""
Chat API endpoints for TariffAI
Provides intelligent chat interface using the orchestrator agent.
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents.orchestrator import OrchestratorAgent
from app.core.responses import create_success_response, create_error_response

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Initialize orchestrator agent
orchestrator = OrchestratorAgent()


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., description="User message", min_length=1, max_length=1000)
    session_id: Optional[str] = Field(None, description="Session ID for context")


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str = Field(..., description="AI response")
    session_id: str = Field(..., description="Session ID")
    intent: Optional[str] = Field(None, description="Detected intent")
    confidence: Optional[float] = Field(None, description="Response confidence")


@router.post("/", response_model=dict)
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint that processes user queries intelligently.
    
    This endpoint uses the orchestrator agent to:
    1. Detect user intent
    2. Route to appropriate specialist agents
    3. Generate comprehensive responses
    """
    try:
        logger.info(f"💬 Chat request: {request.message[:100]}...")
        
        # Process query through orchestrator
        result = await orchestrator.process_query(
            query=request.message,
            session_id=request.session_id
        )
        
        # Extract response data
        if result.get("success"):
            data = result.get("data", {})
            response_text = data.get("response", "I'm sorry, I couldn't process your request.")
            
            return {
                "response": response_text,
                "session_id": result.get("session_id"),
                "intent": data.get("intent"),
                "confidence": data.get("confidence"),
                "success": True,
                "message": result.get("message", "Chat response generated successfully")
            }
        else:
            # Handle error response
            raise HTTPException(
                status_code=400,
                detail=result.get("message", "Failed to process chat request")
            )
            
    except Exception as e:
        logger.error(f"❌ Chat endpoint error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/session/{session_id}")
async def get_session_info(session_id: str):
    """Get information about a chat session."""
    try:
        session_info = orchestrator.get_session_info(session_id)
        if session_info:
            return create_success_response(
                data=session_info,
                message="Session information retrieved successfully"
            )
        else:
            return create_error_response(
                message="Session not found",
                error_code="SESSION_NOT_FOUND"
            )
    except Exception as e:
        logger.error(f"❌ Session info error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear a chat session."""
    try:
        success = orchestrator.clear_session(session_id)
        if success:
            return create_success_response(
                message="Session cleared successfully"
            )
        else:
            return create_error_response(
                message="Session not found",
                error_code="SESSION_NOT_FOUND"
            )
    except Exception as e:
        logger.error(f"❌ Clear session error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming chat endpoint for real-time responses.
    Note: This is a placeholder for future streaming implementation.
    """
    # For now, return the same response as regular chat
    # In the future, this could implement Server-Sent Events or WebSocket
    return await chat_endpoint(request) 