from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File, Body
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import json
import os
import shutil
import pdfplumber
from docx import Document

from app.core.database import get_db
from app.models.chat import ChatSession, ChatMessage
from app.schemas.chat import (
    ChatRequest, ChatResponse, ChatSessionResponse, 
    ChatMessageResponse, ChatSessionCreate
)
from app.services.ai_service import AIService

router = APIRouter()
ai_service = AIService()

@router.post("/send", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Send a message to the AI and get a response"""
    
    # Get or create chat session (simplified without user authentication)
    if request.session_id:
        session = db.query(ChatSession).filter(
            ChatSession.id == request.session_id
        ).first()
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
    else:
        # Create new session with default user_id
        session = ChatSession(
            user_id=1,  # Default user ID
            title=request.session_title or "New Chat"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    
    # Save user message
    user_message = ChatMessage(
        session_id=session.id,
        role="user",
        content=request.message
    )
    db.add(user_message)
    db.commit()
    
    # Get AI response
    try:
        ai_response = await ai_service.get_response(request.message, session.id)
        
        # Save AI response
        assistant_message = ChatMessage(
            session_id=session.id,
            role="assistant",
            content=ai_response
        )
        db.add(assistant_message)
        db.commit()
        
        return ChatResponse(
            message=ai_response,
            session_id=session.id,
            message_id=assistant_message.id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_chat_sessions(
    db: Session = Depends(get_db)
):
    """Get all chat sessions (simplified without user authentication)"""
    sessions = db.query(ChatSession).filter(
        ChatSession.is_active == True
    ).order_by(ChatSession.updated_at.desc()).all()
    
    return sessions

@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
async def get_session_messages(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Get all messages in a specific chat session (simplified without user authentication)"""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.timestamp).all()
    
    return messages

@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Delete a chat session (simplified without user authentication)"""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    session.is_active = False
    db.commit()
    
    return {"message": "Chat session deleted successfully"}

@router.post("/init-knowledge-base")
async def initialize_knowledge_base():
    """Initialize the knowledge base with all reference data in the knowledge_base folder"""
    try:
        # Load all knowledge base files from the folder
        knowledge_base_folder = "./data/knowledge_base"
        loaded_count = await ai_service.vector_store.load_knowledge_base_folder(knowledge_base_folder)
        return {
            "message": f"Knowledge base initialized successfully",
            "documents_loaded": loaded_count,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize knowledge base: {str(e)}")

@router.get("/knowledge-stats")
async def get_knowledge_stats():
    """Get knowledge base statistics"""
    try:
        stats = await ai_service.vector_store.get_collection_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get knowledge stats: {str(e)}")

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, db: Session = Depends(get_db)):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process message and get AI response
            ai_response = await ai_service.get_response(message_data["message"])
            
            # Send response back to client
            await websocket.send_text(json.dumps({
                "message": ai_response,
                "timestamp": str(datetime.utcnow())
            }))
    except WebSocketDisconnect:
        print(f"Client {user_id} disconnected")
    except Exception as e:
        await websocket.send_text(json.dumps({
            "error": str(e)
        }))

@router.post("/upload-knowledge")
async def upload_knowledge_file(file: UploadFile = File(...)):
    """Upload a knowledge file (PDF, TXT, DOC, DOCX), extract text, and add to the knowledge base."""
    allowed_types = ["application/pdf", "text/plain", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]
    ext_map = {"application/pdf": ".pdf", "text/plain": ".txt", "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx", "application/msword": ".doc"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Unsupported file type.")
    # Save file to knowledge_base folder
    kb_folder = "./data/knowledge_base"
    os.makedirs(kb_folder, exist_ok=True)
    file_ext = ext_map.get(file.content_type, "")
    save_path = os.path.join(kb_folder, file.filename)
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # Extract text
    text = ""
    try:
        if file.content_type == "application/pdf":
            with pdfplumber.open(save_path) as pdf:
                text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        elif file.content_type == "text/plain":
            with open(save_path, "r", encoding="utf-8") as f:
                text = f.read()
        elif file.content_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
            doc = Document(save_path)
            text = "\n".join([para.text for para in doc.paragraphs])
        else:
            raise Exception("Unsupported file type for extraction.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract text: {str(e)}")
    # Add to vector store
    if text.strip():
        await ai_service.vector_store.add_document(
            content=text.strip(),
            metadata={"type": "user_upload", "filename": file.filename},
            doc_id=f"user_{file.filename}"
        )
        return {"message": "Knowledge uploaded and indexed successfully."}
    else:
        raise HTTPException(status_code=400, detail="No extractable text found in file.")

@router.post("/upload-text")
async def upload_text_to_knowledge_base(payload: dict = Body(...)):
    """Upload plain text to the knowledge base (for RAG)."""
    text = payload.get('text', '').strip()
    if not text:
        raise HTTPException(status_code=400, detail="No text provided.")
    kb_folder = "./data/knowledge_base"
    os.makedirs(kb_folder, exist_ok=True)
    # Save as a .txt file for persistence
    import uuid
    file_id = str(uuid.uuid4())
    file_path = os.path.join(kb_folder, f'user_{file_id}.txt')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    # Add to vector store
    await ai_service.vector_store.add_document(
        content=text,
        metadata={"type": "user_text", "filename": f'user_{file_id}.txt'},
        doc_id=f'user_text_{file_id}'
    )
    return {"message": "Text added to knowledge base and indexed successfully."} 