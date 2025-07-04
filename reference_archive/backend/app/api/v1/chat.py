"""
Chat API endpoints for TariffAI
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ...core.responses import ChatResponse, ErrorResponse
from ...agents.orchestrator import OrchestratorAgent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

# Initialize orchestrator agent
orchestrator = OrchestratorAgent()


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str
    session_id: Optional[str] = None


class ChatHistoryRequest(BaseModel):
    """Chat history request model"""
    session_id: str


@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint for tariff-related queries
    """
    try:
        if not request.message.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be empty"
            )
        
        # Process the query through the orchestrator
        response = await orchestrator.process_query(
            message=request.message,
            session_id=request.session_id
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/session/{session_id}")
async def get_session_info(session_id: str):
    """
    Get session information
    """
    try:
        session_info = orchestrator.get_session_info(session_id)
        if not session_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        return {
            "success": True,
            "session_id": session_id,
            "info": session_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """
    Clear a chat session
    """
    try:
        success = orchestrator.clear_session(session_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        return {
            "success": True,
            "message": "Session cleared successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/health")
async def chat_health_check():
    """
    Health check for chat service
    """
    try:
        # Basic health check
        return {
            "success": True,
            "service": "chat",
            "status": "healthy",
            "orchestrator_initialized": True
        }
        
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service unhealthy"
        ) 