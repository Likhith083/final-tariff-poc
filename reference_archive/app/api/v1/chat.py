from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.services.ai_service import AIService
from app.services.chroma_service import ChromaService
from app.services.hts_service import HTSService
from app.core.responses import ChatResponse, ErrorResponse
from app.db.models import ChatSession, ChatMessage
from sqlalchemy import select
import uuid
from datetime import datetime
from loguru import logger

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    context_type: Optional[str] = None  # 'hts', 'materials', 'general'

class ChatSessionRequest(BaseModel):
    session_id: str

@router.post("/", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send a message to the AI assistant"""
    try:
        # Initialize services
        ai_service = AIService()
        chroma_service = ChromaService()
        hts_service = HTSService()
        
        # Get or create session
        session_id = request.session_id or str(uuid.uuid4())
        session = await _get_or_create_session(db, session_id)
        
        # Store user message
        await _store_message(db, session_id, "user", request.message)
        
        # Get relevant context based on message content
        context = await _get_context(request.message, chroma_service, hts_service)
        
        # Generate AI response
        ai_response = await ai_service.generate_response(request.message, context)
        
        # Store AI response
        await _store_message(
            db, 
            session_id, 
            "assistant", 
            ai_response['response'],
            {
                'confidence': ai_response.get('confidence', 0.0),
                'model': ai_response.get('model', ''),
                'sources': context
            }
        )
        
        # Update session
        await _update_session(db, session_id)
        
        return ChatResponse(
            success=True,
            message="Message processed successfully",
            session_id=session_id,
            response=ai_response['response'],
            confidence=ai_response.get('confidence', 0.0),
            sources=context
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}", response_model=ChatResponse)
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get chat session information"""
    try:
        # Get session
        session = await _get_session(db, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get messages
        messages = await _get_session_messages(db, session_id)
        
        return ChatResponse(
            success=True,
            message="Session retrieved successfully",
            session_id=session_id,
            response=f"Session has {len(messages)} messages",
            confidence=1.0,
            data={
                'session': {
                    'id': session.session_id,
                    'created_at': session.created_at.isoformat(),
                    'updated_at': session.updated_at.isoformat(),
                    'is_active': session.is_active
                },
                'messages': messages
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/session/{session_id}")
async def clear_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Clear a chat session"""
    try:
        # Get session
        session = await _get_session(db, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Mark session as inactive
        session.is_active = False
        await db.commit()
        
        return {"success": True, "message": "Session cleared successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Clear session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def chat_health():
    """Check chat service health"""
    try:
        ai_service = AIService()
        health = await ai_service.check_health()
        
        return {
            "service": "chat",
            "status": "healthy" if health['healthy'] else "unhealthy",
            "ai_service": health
        }
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "service": "chat",
            "status": "unhealthy",
            "error": str(e)
        }

async def _get_or_create_session(db: AsyncSession, session_id: str) -> ChatSession:
    """Get existing session or create new one"""
    result = await db.execute(
        select(ChatSession).where(ChatSession.session_id == session_id)
    )
    session = result.scalar_one_or_none()
    
    if not session:
        session = ChatSession(session_id=session_id)
        db.add(session)
        await db.commit()
        await db.refresh(session)
    
    return session

async def _get_session(db: AsyncSession, session_id: str) -> Optional[ChatSession]:
    """Get session by ID"""
    result = await db.execute(
        select(ChatSession).where(ChatSession.session_id == session_id)
    )
    return result.scalar_one_or_none()

async def _store_message(
    db: AsyncSession, 
    session_id: str, 
    message_type: str, 
    content: str, 
    metadata: Optional[Dict] = None
):
    """Store a message in the database"""
    message = ChatMessage(
        session_id=session_id,
        message_type=message_type,
        content=content,
        metadata=metadata
    )
    db.add(message)
    await db.commit()

async def _update_session(db: AsyncSession, session_id: str):
    """Update session timestamp"""
    session = await _get_session(db, session_id)
    if session:
        session.updated_at = datetime.now()
        await db.commit()

async def _get_session_messages(db: AsyncSession, session_id: str) -> List[Dict]:
    """Get all messages for a session"""
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.timestamp)
    )
    messages = result.scalars().all()
    
    return [
        {
            'id': msg.id,
            'type': msg.message_type,
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat(),
            'metadata': msg.metadata
        }
        for msg in messages
    ]

async def _get_context(
    message: str, 
    chroma_service: ChromaService, 
    hts_service: HTSService
) -> List[Dict[str, Any]]:
    """Get relevant context for the message"""
    context = []
    
    try:
        # Check if message is about HTS codes
        if any(keyword in message.lower() for keyword in ['hts', 'code', 'tariff', 'classification']):
            hts_results = await hts_service.search_hts_codes(message, 3)
            context.extend(hts_results)
        
        # Check if message is about materials
        if any(keyword in message.lower() for keyword in ['material', 'composition', 'fabric', 'textile']):
            material_results = await chroma_service.search_materials(message, 3)
            context.extend(material_results)
        
        # Check if message is about AD/CVD
        if any(keyword in message.lower() for keyword in ['ad/cvd', 'antidumping', 'countervailing', 'duty']):
            adcvd_results = await chroma_service.search_adcvd_faq(message, 3)
            context.extend(adcvd_results)
        
    except Exception as e:
        logger.error(f"Error getting context: {e}")
    
    return context
