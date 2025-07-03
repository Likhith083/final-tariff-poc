import pytest
from httpx import AsyncClient
from app.db.models import ChatSession, ChatMessage
from datetime import datetime

@pytest.mark.api
class TestChatMessage:
    """Test chat message endpoints."""
    
    async def test_send_message_success(self, client: AsyncClient, db_session):
        """Test successful message sending."""
        response = await client.post("/api/v1/chat/", json={
            "message": "What is the tariff rate for laptop computers?",
            "session_id": "test-session-123",
            "context_type": "hts"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["session_id"] == "test-session-123"
        assert "response" in data
        assert "confidence" in data
    
    async def test_send_message_without_session_id(self, client: AsyncClient, db_session):
        """Test message sending without session ID (should create new session)."""
        response = await client.post("/api/v1/chat/", json={
            "message": "Hello, how can you help me?",
            "context_type": "general"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["session_id"] is not None
        assert len(data["session_id"]) > 0
    
    async def test_send_message_empty_message(self, client: AsyncClient):
        """Test message sending with empty message."""
        response = await client.post("/api/v1/chat/", json={
            "message": "",
            "session_id": "test-session-123"
        })
        
        assert response.status_code == 422  # Validation error
    
    async def test_send_message_hts_context(self, client: AsyncClient, db_session):
        """Test message with HTS context."""
        response = await client.post("/api/v1/chat/", json={
            "message": "Find HTS codes for electronic devices",
            "session_id": "test-session-hts",
            "context_type": "hts"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["context_type"] == "hts"
    
    async def test_send_message_materials_context(self, client: AsyncClient, db_session):
        """Test message with materials context."""
        response = await client.post("/api/v1/chat/", json={
            "message": "Analyze cotton fabric composition",
            "session_id": "test-session-materials",
            "context_type": "materials"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["context_type"] == "materials"

@pytest.mark.api
class TestChatSession:
    """Test chat session endpoints."""
    
    async def test_get_session_success(self, client: AsyncClient, db_session):
        """Test successful session retrieval."""
        # Create test session
        session = ChatSession(
            session_id="test-session-456",
            user_id="test-user",
            is_active=True
        )
        db_session.add(session)
        
        # Add test messages
        messages = [
            ChatMessage(
                session_id="test-session-456",
                message_type="user",
                content="Hello",
                timestamp=datetime.now()
            ),
            ChatMessage(
                session_id="test-session-456",
                message_type="assistant",
                content="Hi! How can I help you?",
                timestamp=datetime.now()
            )
        ]
        for msg in messages:
            db_session.add(msg)
        
        await db_session.commit()
        
        response = await client.get("/api/v1/chat/session/test-session-456")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["session_id"] == "test-session-456"
        assert len(data["data"]["messages"]) == 2
    
    async def test_get_session_not_found(self, client: AsyncClient):
        """Test session retrieval for non-existent session."""
        response = await client.get("/api/v1/chat/session/nonexistent-session")
        
        assert response.status_code == 404
    
    async def test_clear_session_success(self, client: AsyncClient, db_session):
        """Test successful session clearing."""
        # Create test session
        session = ChatSession(
            session_id="test-session-clear",
            user_id="test-user",
            is_active=True
        )
        db_session.add(session)
        await db_session.commit()
        
        response = await client.delete("/api/v1/chat/session/test-session-clear")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Session cleared successfully"
    
    async def test_clear_session_not_found(self, client: AsyncClient):
        """Test clearing non-existent session."""
        response = await client.delete("/api/v1/chat/session/nonexistent-session")
        
        assert response.status_code == 404

@pytest.mark.api
class TestChatHealth:
    """Test chat service health check endpoint."""
    
    async def test_chat_health(self, client: AsyncClient):
        """Test chat service health check."""
        response = await client.get("/api/v1/chat/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "chat"
        assert "status" in data
        assert "ai_service" in data

@pytest.mark.api
class TestChatContext:
    """Test chat context functionality."""
    
    async def test_chat_with_hts_context(self, client: AsyncClient, db_session):
        """Test chat with HTS-related context."""
        response = await client.post("/api/v1/chat/", json={
            "message": "What HTS code should I use for smartphones?",
            "session_id": "test-session-hts-context",
            "context_type": "hts"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # Should have sources related to HTS codes
        assert "sources" in data
    
    async def test_chat_with_materials_context(self, client: AsyncClient, db_session):
        """Test chat with materials-related context."""
        response = await client.post("/api/v1/chat/", json={
            "message": "What are the best material alternatives for cotton?",
            "session_id": "test-session-materials-context",
            "context_type": "materials"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # Should have sources related to materials
        assert "sources" in data
    
    async def test_chat_with_adcvd_context(self, client: AsyncClient, db_session):
        """Test chat with AD/CVD-related context."""
        response = await client.post("/api/v1/chat/", json={
            "message": "What are antidumping duties?",
            "session_id": "test-session-adcvd-context",
            "context_type": "general"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # Should have sources related to AD/CVD
        assert "sources" in data

@pytest.mark.api
class TestChatMessageStorage:
    """Test chat message storage functionality."""
    
    async def test_message_storage_in_database(self, client: AsyncClient, db_session):
        """Test that messages are properly stored in database."""
        session_id = "test-storage-session"
        
        # Send a message
        response = await client.post("/api/v1/chat/", json={
            "message": "Test message for storage",
            "session_id": session_id
        })
        
        assert response.status_code == 200
        
        # Check that session was created
        session_result = await db_session.execute(
            "SELECT * FROM chat_sessions WHERE session_id = :session_id",
            {"session_id": session_id}
        )
        session = session_result.fetchone()
        assert session is not None
        
        # Check that messages were stored
        messages_result = await db_session.execute(
            "SELECT * FROM chat_messages WHERE session_id = :session_id",
            {"session_id": session_id}
        )
        messages = messages_result.fetchall()
        assert len(messages) >= 2  # User message + AI response
    
    async def test_message_metadata_storage(self, client: AsyncClient, db_session):
        """Test that message metadata is properly stored."""
        session_id = "test-metadata-session"
        
        response = await client.post("/api/v1/chat/", json={
            "message": "Test message with metadata",
            "session_id": session_id
        })
        
        assert response.status_code == 200
        
        # Check that metadata was stored
        messages_result = await db_session.execute(
            "SELECT message_metadata FROM chat_messages WHERE session_id = :session_id AND message_type = 'assistant'",
            {"session_id": session_id}
        )
        message = messages_result.fetchone()
        assert message is not None
        assert message[0] is not None  # metadata should not be null 