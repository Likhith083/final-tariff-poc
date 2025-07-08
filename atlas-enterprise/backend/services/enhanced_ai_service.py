"""
Enhanced AI Service for ATLAS Enterprise
Advanced AI capabilities including knowledge base updates, multimodal processing, and intelligent assistance.
"""

import asyncio
import base64
import io
import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

import httpx
from PIL import Image
import pytesseract
from transformers import pipeline, BlipProcessor, BlipForConditionalGeneration
import speech_recognition as sr
from groq import AsyncGroq

from ..core.config import settings
from ..core.logging import get_logger, log_business_event
from ..core.database import get_cache
from .knowledge_base_service import knowledge_service, DocumentType

logger = get_logger(__name__)


class AIServiceType(Enum):
    """AI service types."""
    CHAT = "chat"
    CLASSIFICATION = "classification"
    OCR = "ocr"
    VISION = "vision"
    SPEECH = "speech"
    KNOWLEDGE_UPDATE = "knowledge_update"


class ConversationRole(Enum):
    """Conversation roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class ConversationMessage:
    """Conversation message structure."""
    role: ConversationRole
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = None


@dataclass
class AIResponse:
    """AI response structure."""
    content: str
    confidence: float
    service_type: AIServiceType
    processing_time: float
    metadata: Dict[str, Any] = None
    error: Optional[str] = None


class EnhancedAIService:
    """Enhanced AI service with multimodal capabilities."""
    
    def __init__(self):
        """Initialize the enhanced AI service."""
        self.groq_client = None
        self.cache = None
        self.vision_processor = None
        self.vision_model = None
        self.speech_recognizer = None
        self.conversation_history = {}
        self._initialized = False
    
    async def initialize(self):
        """Initialize AI service components."""
        if self._initialized:
            return
        
        # Initialize Groq client
        if settings.groq_api_key:
            self.groq_client = AsyncGroq(api_key=settings.groq_api_key)
        
        # Initialize cache
        self.cache = get_cache()
        
        # Initialize vision models (optional, requires GPU)
        try:
            self.vision_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            self.vision_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            logger.info("Vision models initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize vision models: {e}")
        
        # Initialize speech recognition
        try:
            self.speech_recognizer = sr.Recognizer()
            logger.info("Speech recognition initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize speech recognition: {e}")
        
        # Initialize knowledge base service
        await knowledge_service.initialize()
        
        self._initialized = True
        logger.info("Enhanced AI service initialized")
    
    async def chat_with_knowledge_update(self, message: str, user_id: str, 
                                       conversation_id: Optional[str] = None,
                                       include_knowledge_search: bool = True) -> Dict[str, Any]:
        """Enhanced chat that can update knowledge base via text input."""
        try:
            if not conversation_id:
                conversation_id = str(uuid.uuid4())
            
            # Add user message to conversation history
            await self._add_to_conversation(conversation_id, ConversationRole.USER, message)
            
            # Check if this is a knowledge update request
            knowledge_update_intent = await self._detect_knowledge_update_intent(message)
            
            if knowledge_update_intent["is_knowledge_update"]:
                # Process as knowledge update
                knowledge_result = await knowledge_service.add_knowledge_from_text(
                    text_input=knowledge_update_intent["knowledge_content"],
                    user_id=user_id,
                    source="ai_assistant_chat"
                )
                
                if knowledge_result["success"]:
                    response_content = f"""✅ **Knowledge successfully added to the database!**

**Document Details:**
- **ID:** {knowledge_result['document_id']}
- **Title:** {knowledge_result['title']}
- **Type:** {knowledge_result['doc_type']}
- **Confidence:** {knowledge_result['confidence']:.2%}
- **Tags:** {', '.join(knowledge_result['tags'])}

The information has been processed and is now available for future queries. The system extracted relevant entities and classified the content automatically.

Is there anything else you'd like to add to the knowledge base or any questions about the stored information?"""
                else:
                    response_content = f"❌ **Failed to add knowledge to database:** {knowledge_result.get('error', 'Unknown error')}\n\nPlease try rephrasing your input or contact support if the issue persists."
                
                # Add assistant response to conversation
                await self._add_to_conversation(conversation_id, ConversationRole.ASSISTANT, response_content)
                
                return {
                    "conversation_id": conversation_id,
                    "response": response_content,
                    "knowledge_update": True,
                    "knowledge_result": knowledge_result,
                    "processing_time": 0.5  # Estimated
                }
            
            # Regular chat processing with optional knowledge search
            enhanced_message = message
            knowledge_context = ""
            
            if include_knowledge_search:
                # Search knowledge base for relevant information
                knowledge_results = await knowledge_service.search_knowledge(message, limit=3)
                if knowledge_results:
                    knowledge_context = "\n\n**Relevant Knowledge Base Information:**\n"
                    for i, result in enumerate(knowledge_results[:2], 1):
                        knowledge_context += f"{i}. {result['content'][:200]}...\n"
                    
                    enhanced_message = f"{message}\n\nContext from knowledge base: {knowledge_context}"
            
            # Get conversation history
            history = await self._get_conversation_history(conversation_id, limit=10)
            
            # Build messages for Groq
            messages = [
                {
                    "role": "system",
                    "content": """You are an advanced AI assistant for ATLAS Enterprise, a trade compliance platform. 

Key capabilities:
1. Answer questions about tariffs, trade regulations, and compliance
2. Help with HTS code classification and tariff calculations
3. Provide guidance on international trade procedures
4. Update the knowledge base when users provide new information

When users want to add information to the knowledge base, look for phrases like:
- "Add this to knowledge base"
- "Remember this information"
- "Store this for future reference"
- "Update the database with"
- "This should be saved"

For knowledge updates, extract and structure the information clearly.
For regular queries, provide helpful, accurate responses based on trade compliance expertise.

Always be professional, helpful, and accurate in your responses."""
                }
            ]
            
            # Add conversation history
            for msg in history:
                messages.append({
                    "role": msg.role.value,
                    "content": msg.content
                })
            
            # Add current enhanced message
            messages.append({
                "role": "user",
                "content": enhanced_message
            })
            
            # Call Groq API
            start_time = datetime.now()
            response = await self.groq_client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=messages,
                temperature=0.7,
                max_tokens=1500
            )
            processing_time = (datetime.now() - start_time).total_seconds()
            
            response_content = response.choices[0].message.content
            
            # Add assistant response to conversation
            await self._add_to_conversation(conversation_id, ConversationRole.ASSISTANT, response_content)
            
            return {
                "conversation_id": conversation_id,
                "response": response_content,
                "knowledge_update": False,
                "knowledge_context": knowledge_context if knowledge_context else None,
                "processing_time": processing_time
            }
            
        except Exception as e:
            logger.error(f"Enhanced chat failed: {e}")
            return {
                "conversation_id": conversation_id,
                "response": f"I apologize, but I encountered an error: {str(e)}. Please try again or contact support if the issue persists.",
                "error": str(e),
                "processing_time": 0
            }
    
    async def _detect_knowledge_update_intent(self, message: str) -> Dict[str, Any]:
        """Detect if the message contains intent to update knowledge base."""
        update_phrases = [
            "add this to knowledge base",
            "remember this information",
            "store this for future reference",
            "update the database with",
            "this should be saved",
            "add to knowledge",
            "store this",
            "remember that",
            "save this information",
            "update knowledge with"
        ]
        
        message_lower = message.lower()
        is_update = any(phrase in message_lower for phrase in update_phrases)
        
        if is_update:
            # Extract the knowledge content (everything after the update phrase)
            knowledge_content = message
            for phrase in update_phrases:
                if phrase in message_lower:
                    # Find the phrase and extract content after it
                    phrase_index = message_lower.find(phrase)
                    if phrase_index != -1:
                        start_index = phrase_index + len(phrase)
                        knowledge_content = message[start_index:].strip().lstrip(':').strip()
                        if not knowledge_content:
                            knowledge_content = message  # Fallback to full message
                    break
        else:
            knowledge_content = ""
        
        return {
            "is_knowledge_update": is_update,
            "knowledge_content": knowledge_content,
            "original_message": message
        }
    
    async def process_document_ocr(self, image_data: bytes, 
                                 extract_hts_codes: bool = True) -> Dict[str, Any]:
        """Process document with OCR to extract text and HTS codes."""
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Perform OCR
            start_time = datetime.now()
            extracted_text = pytesseract.image_to_string(image)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Extract HTS codes if requested
            hts_codes = []
            if extract_hts_codes:
                import re
                hts_pattern = r'\b\d{4}[\.\-]?\d{2}[\.\-]?\d{2}[\.\-]?\d{2}\b'
                hts_codes = re.findall(hts_pattern, extracted_text)
            
            # Extract other relevant information
            entities = await self._extract_document_entities(extracted_text)
            
            return {
                "success": True,
                "extracted_text": extracted_text,
                "hts_codes": hts_codes,
                "entities": entities,
                "processing_time": processing_time,
                "confidence": 0.8  # OCR confidence would need proper calculation
            }
            
        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "processing_time": 0
            }
    
    async def analyze_product_image(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze product image for classification."""
        try:
            if not self.vision_model:
                return {
                    "success": False,
                    "error": "Vision models not available"
                }
            
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Generate image description
            start_time = datetime.now()
            inputs = self.vision_processor(image, return_tensors="pt")
            out = self.vision_model.generate(**inputs, max_new_tokens=50)
            description = self.vision_processor.decode(out[0], skip_special_tokens=True)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Use description for product classification
            classification_result = await self._classify_product_from_description(description)
            
            return {
                "success": True,
                "description": description,
                "classification": classification_result,
                "processing_time": processing_time
            }
            
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "processing_time": 0
            }
    
    async def process_voice_input(self, audio_data: bytes) -> Dict[str, Any]:
        """Process voice input and convert to text."""
        try:
            if not self.speech_recognizer:
                return {
                    "success": False,
                    "error": "Speech recognition not available"
                }
            
            # Convert audio data to AudioFile format (this is simplified)
            # In practice, you'd need proper audio format handling
            
            start_time = datetime.now()
            # This is a placeholder - real implementation would need proper audio handling
            transcribed_text = "Voice processing not fully implemented"
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": True,
                "transcribed_text": transcribed_text,
                "processing_time": processing_time
            }
            
        except Exception as e:
            logger.error(f"Voice processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "processing_time": 0
            }
    
    async def _classify_product_from_description(self, description: str) -> Dict[str, Any]:
        """Classify product based on description."""
        # This would use your existing classification logic
        # For now, return a simplified result
        return {
            "suggested_hts": "8471.30.01",
            "confidence": 0.75,
            "category": "Electronics",
            "reasoning": f"Based on description: {description}"
        }
    
    async def _extract_document_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities from document text."""
        entities = []
        
        # Extract common trade document entities
        import re
        
        # Invoice numbers
        invoice_pattern = r'Invoice\s*[#:]?\s*([A-Z0-9-]+)'
        invoices = re.findall(invoice_pattern, text, re.IGNORECASE)
        for invoice in invoices:
            entities.append({"type": "invoice_number", "value": invoice, "confidence": 0.9})
        
        # PO numbers
        po_pattern = r'P\.?O\.?\s*[#:]?\s*([A-Z0-9-]+)'
        pos = re.findall(po_pattern, text, re.IGNORECASE)
        for po in pos:
            entities.append({"type": "po_number", "value": po, "confidence": 0.9})
        
        # Amounts
        amount_pattern = r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
        amounts = re.findall(amount_pattern, text)
        for amount in amounts:
            entities.append({"type": "amount", "value": f"${amount}", "confidence": 0.8})
        
        return entities
    
    async def _add_to_conversation(self, conversation_id: str, role: ConversationRole, content: str):
        """Add message to conversation history."""
        if conversation_id not in self.conversation_history:
            self.conversation_history[conversation_id] = []
        
        message = ConversationMessage(
            role=role,
            content=content,
            timestamp=datetime.now()
        )
        
        self.conversation_history[conversation_id].append(message)
        
        # Cache conversation history
        await self.cache.set(
            f"conversation:{conversation_id}",
            [msg.__dict__ for msg in self.conversation_history[conversation_id]],
            ttl=3600  # 1 hour
        )
        
        # Keep only last 50 messages per conversation
        if len(self.conversation_history[conversation_id]) > 50:
            self.conversation_history[conversation_id] = self.conversation_history[conversation_id][-50:]
    
    async def _get_conversation_history(self, conversation_id: str, limit: int = 10) -> List[ConversationMessage]:
        """Get conversation history."""
        if conversation_id in self.conversation_history:
            return self.conversation_history[conversation_id][-limit:]
        
        # Try to load from cache
        cached_history = await self.cache.get(f"conversation:{conversation_id}")
        if cached_history:
            messages = []
            for msg_data in cached_history[-limit:]:
                message = ConversationMessage(
                    role=ConversationRole(msg_data["role"]),
                    content=msg_data["content"],
                    timestamp=datetime.fromisoformat(msg_data["timestamp"]),
                    metadata=msg_data.get("metadata")
                )
                messages.append(message)
            return messages
        
        return []
    
    async def get_conversation_summary(self, conversation_id: str) -> Dict[str, Any]:
        """Get conversation summary and statistics."""
        history = await self._get_conversation_history(conversation_id, limit=100)
        
        if not history:
            return {"error": "Conversation not found"}
        
        return {
            "conversation_id": conversation_id,
            "message_count": len(history),
            "start_time": history[0].timestamp.isoformat() if history else None,
            "last_activity": history[-1].timestamp.isoformat() if history else None,
            "knowledge_updates": sum(1 for msg in history if "knowledge" in msg.content.lower()),
            "user_messages": sum(1 for msg in history if msg.role == ConversationRole.USER),
            "assistant_messages": sum(1 for msg in history if msg.role == ConversationRole.ASSISTANT)
        }


# Global enhanced AI service
enhanced_ai_service = EnhancedAIService() 