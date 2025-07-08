"""
Knowledge Base Service for ATLAS Enterprise
Advanced knowledge management with AI-powered updates via text input.
"""

import asyncio
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

import chromadb
from sentence_transformers import SentenceTransformer
from transformers import pipeline

from ..core.database import get_vector_store, get_cache
from ..core.logging import get_logger, log_business_event
from ..core.config import settings

logger = get_logger(__name__)


class DocumentType(Enum):
    """Document types in knowledge base."""
    TARIFF_INFO = "tariff_info"
    REGULATION = "regulation"
    PROCEDURE = "procedure"
    FAQ = "faq"
    POLICY = "policy"
    ANNOUNCEMENT = "announcement"
    USER_INPUT = "user_input"


class DocumentStatus(Enum):
    """Document status in knowledge base."""
    ACTIVE = "active"
    DRAFT = "draft"
    ARCHIVED = "archived"
    PENDING_REVIEW = "pending_review"


@dataclass
class KnowledgeDocument:
    """Knowledge base document structure."""
    id: str
    title: str
    content: str
    doc_type: DocumentType
    status: DocumentStatus
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    version: int
    tags: List[str]
    confidence_score: float = 0.0
    source: str = "system"
    author: str = "system"


class KnowledgeBaseService:
    """Advanced knowledge base management service."""
    
    def __init__(self):
        """Initialize knowledge base service."""
        self.vector_store = None
        self.cache = None
        self.embedding_model = None
        self.nlp_pipeline = None
        self.collection_name = "atlas_knowledge_base"
        self._initialized = False
    
    async def initialize(self):
        """Initialize the knowledge base service."""
        if self._initialized:
            return
        
        self.vector_store = get_vector_store()
        self.cache = get_cache()
        
        # Initialize AI models for text processing
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.nlp_pipeline = pipeline(
                "text-classification",
                model="facebook/bart-large-mnli",
                return_all_scores=True
            )
            logger.info("AI models initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize AI models: {e}")
            # Fallback to basic text processing
        
        self._initialized = True
        logger.info("Knowledge base service initialized")
    
    async def add_knowledge_from_text(self, text_input: str, user_id: str = "system", 
                                    source: str = "ai_assistant") -> Dict[str, Any]:
        """Add knowledge to the base from user text input via AI assistant."""
        try:
            # Process and analyze the text input
            processed_data = await self._process_text_input(text_input, user_id, source)
            
            # Extract entities and classify content
            entities = await self._extract_entities(text_input)
            doc_type = await self._classify_document_type(text_input)
            
            # Generate document
            document = KnowledgeDocument(
                id=str(uuid.uuid4()),
                title=processed_data["title"],
                content=processed_data["content"],
                doc_type=doc_type,
                status=DocumentStatus.ACTIVE,
                metadata={
                    "entities": entities,
                    "confidence": processed_data["confidence"],
                    "processing_method": processed_data["method"],
                    "user_input": text_input[:500],  # Store snippet of original input
                    "extracted_topics": processed_data["topics"]
                },
                created_at=datetime.now(),
                updated_at=datetime.now(),
                version=1,
                tags=processed_data["tags"],
                confidence_score=processed_data["confidence"],
                source=source,
                author=user_id
            )
            
            # Add to vector store
            success = await self.vector_store.add_document(
                collection_name=self.collection_name,
                document=document.content,
                metadata={
                    "id": document.id,
                    "title": document.title,
                    "doc_type": document.doc_type.value,
                    "status": document.status.value,
                    "created_at": document.created_at.isoformat(),
                    "tags": ",".join(document.tags),
                    "confidence": document.confidence_score,
                    "source": document.source,
                    "author": document.author
                },
                doc_id=document.id
            )
            
            if success:
                # Cache the document
                await self.cache.set(
                    f"knowledge_doc:{document.id}",
                    document.__dict__,
                    ttl=86400  # 24 hours
                )
                
                # Invalidate search cache
                await self.cache.invalidate_pattern("knowledge_search:*")
                
                # Log the event
                await log_business_event(
                    "knowledge_base_update",
                    {
                        "document_id": document.id,
                        "user_id": user_id,
                        "source": source,
                        "doc_type": doc_type.value,
                        "confidence": document.confidence_score
                    }
                )
                
                return {
                    "success": True,
                    "document_id": document.id,
                    "title": document.title,
                    "confidence": document.confidence_score,
                    "doc_type": doc_type.value,
                    "tags": document.tags,
                    "message": "Knowledge successfully added to the database"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to store document in vector database"
                }
                
        except Exception as e:
            logger.error(f"Failed to add knowledge from text: {e}")
            return {
                "success": False,
                "error": f"Processing failed: {str(e)}"
            }
    
    async def _process_text_input(self, text: str, user_id: str, source: str) -> Dict[str, Any]:
        """Process and analyze text input to extract structured information."""
        # Clean and normalize text
        cleaned_text = text.strip()
        
        # Extract title (first sentence or first 100 chars)
        sentences = cleaned_text.split('.')
        title = sentences[0][:100] if sentences else cleaned_text[:100]
        
        # Analyze content structure
        if len(cleaned_text) < 50:
            method = "short_text"
            confidence = 0.6
        elif any(keyword in cleaned_text.lower() for keyword in 
                ['tariff', 'hts', 'duty', 'customs', 'trade']):
            method = "trade_specific"
            confidence = 0.9
        else:
            method = "general_processing"
            confidence = 0.7
        
        # Extract topics and tags
        topics = await self._extract_topics(cleaned_text)
        tags = await self._generate_tags(cleaned_text, topics)
        
        return {
            "title": title,
            "content": cleaned_text,
            "method": method,
            "confidence": confidence,
            "topics": topics,
            "tags": tags
        }
    
    async def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities from text."""
        entities = []
        
        # Simple pattern-based entity extraction
        import re
        
        # HTS codes
        hts_pattern = r'\b\d{4}[\.\-]?\d{2}[\.\-]?\d{2}[\.\-]?\d{2}\b'
        hts_matches = re.findall(hts_pattern, text)
        for hts in hts_matches:
            entities.append({
                "text": hts,
                "type": "HTS_CODE",
                "confidence": 0.95
            })
        
        # Country codes
        country_pattern = r'\b[A-Z]{2}\b'
        country_matches = re.findall(country_pattern, text)
        for country in country_matches:
            entities.append({
                "text": country,
                "type": "COUNTRY_CODE",
                "confidence": 0.7
            })
        
        # Percentages (likely tariff rates)
        percentage_pattern = r'\b\d+\.?\d*\s*%'
        percentage_matches = re.findall(percentage_pattern, text)
        for percentage in percentage_matches:
            entities.append({
                "text": percentage,
                "type": "TARIFF_RATE",
                "confidence": 0.8
            })
        
        return entities
    
    async def _classify_document_type(self, text: str) -> DocumentType:
        """Classify the document type based on content."""
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in ['tariff', 'duty', 'rate', 'hts']):
            return DocumentType.TARIFF_INFO
        elif any(keyword in text_lower for keyword in ['regulation', 'rule', 'law']):
            return DocumentType.REGULATION
        elif any(keyword in text_lower for keyword in ['procedure', 'process', 'step']):
            return DocumentType.PROCEDURE
        elif any(keyword in text_lower for keyword in ['question', 'answer', 'faq', 'how to']):
            return DocumentType.FAQ
        elif any(keyword in text_lower for keyword in ['policy', 'guideline']):
            return DocumentType.POLICY
        elif any(keyword in text_lower for keyword in ['announcement', 'update', 'news']):
            return DocumentType.ANNOUNCEMENT
        else:
            return DocumentType.USER_INPUT
    
    async def _extract_topics(self, text: str) -> List[str]:
        """Extract main topics from text."""
        # Simple keyword-based topic extraction
        trade_keywords = {
            'import': ['import', 'importing', 'imports'],
            'export': ['export', 'exporting', 'exports'],
            'tariff': ['tariff', 'duty', 'tax', 'rate'],
            'classification': ['classification', 'classify', 'hts', 'code'],
            'compliance': ['compliance', 'regulation', 'rule'],
            'documentation': ['document', 'paperwork', 'certificate'],
            'shipping': ['shipping', 'freight', 'transport', 'logistics'],
            'customs': ['customs', 'border', 'clearance']
        }
        
        text_lower = text.lower()
        topics = []
        
        for topic, keywords in trade_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics[:5]  # Limit to top 5 topics
    
    async def _generate_tags(self, text: str, topics: List[str]) -> List[str]:
        """Generate tags for the document."""
        tags = set(topics)  # Start with topics
        
        # Add date-based tags
        tags.add(f"year_{datetime.now().year}")
        tags.add(f"month_{datetime.now().strftime('%B').lower()}")
        
        # Add length-based tags
        if len(text) < 100:
            tags.add("short")
        elif len(text) > 1000:
            tags.add("detailed")
        else:
            tags.add("medium")
        
        return list(tags)
    
    async def search_knowledge(self, query: str, limit: int = 10, 
                             doc_type: Optional[DocumentType] = None) -> List[Dict[str, Any]]:
        """Search the knowledge base."""
        try:
            # Check cache first
            cache_key = f"knowledge_search:{hashlib.md5(query.encode()).hexdigest()}:{limit}:{doc_type}"
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # Search in vector store
            results = await self.vector_store.search_documents(
                collection_name=self.collection_name,
                query=query,
                n_results=limit
            )
            
            # Filter by document type if specified
            if doc_type:
                results = [r for r in results if r.get("metadata", {}).get("doc_type") == doc_type.value]
            
            # Enhance results with cached document data
            enhanced_results = []
            for result in results:
                doc_id = result.get("metadata", {}).get("id")
                if doc_id:
                    cached_doc = await self.cache.get(f"knowledge_doc:{doc_id}")
                    if cached_doc:
                        result["document"] = cached_doc
                
                enhanced_results.append(result)
            
            # Cache the results
            await self.cache.set(cache_key, enhanced_results, ttl=1800)  # 30 minutes
            
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Failed to search knowledge base: {e}")
            return []
    
    async def update_knowledge(self, document_id: str, updates: Dict[str, Any], 
                             user_id: str = "system") -> Dict[str, Any]:
        """Update existing knowledge base document."""
        try:
            # Get existing document
            cached_doc = await self.cache.get(f"knowledge_doc:{document_id}")
            if not cached_doc:
                return {"success": False, "error": "Document not found"}
            
            # Update document fields
            for key, value in updates.items():
                if key in ["title", "content", "tags", "status"]:
                    cached_doc[key] = value
            
            cached_doc["updated_at"] = datetime.now().isoformat()
            cached_doc["version"] += 1
            
            # Update in vector store
            success = await self.vector_store.update_document(
                collection_name=self.collection_name,
                doc_id=document_id,
                document=cached_doc["content"],
                metadata={
                    "id": document_id,
                    "title": cached_doc["title"],
                    "doc_type": cached_doc["doc_type"],
                    "status": cached_doc["status"],
                    "updated_at": cached_doc["updated_at"],
                    "tags": ",".join(cached_doc.get("tags", [])),
                    "version": cached_doc["version"]
                }
            )
            
            if success:
                # Update cache
                await self.cache.set(f"knowledge_doc:{document_id}", cached_doc, ttl=86400)
                
                # Invalidate search cache
                await self.cache.invalidate_pattern("knowledge_search:*")
                
                return {"success": True, "document_id": document_id, "version": cached_doc["version"]}
            else:
                return {"success": False, "error": "Failed to update in vector store"}
                
        except Exception as e:
            logger.error(f"Failed to update knowledge: {e}")
            return {"success": False, "error": str(e)}
    
    async def delete_knowledge(self, document_id: str, user_id: str = "system") -> Dict[str, Any]:
        """Delete knowledge base document."""
        try:
            # Delete from vector store
            success = await self.vector_store.delete_document(
                collection_name=self.collection_name,
                doc_id=document_id
            )
            
            if success:
                # Remove from cache
                await self.cache.delete(f"knowledge_doc:{document_id}")
                
                # Invalidate search cache
                await self.cache.invalidate_pattern("knowledge_search:*")
                
                # Log the event
                await log_business_event(
                    "knowledge_base_delete",
                    {"document_id": document_id, "user_id": user_id}
                )
                
                return {"success": True, "document_id": document_id}
            else:
                return {"success": False, "error": "Failed to delete from vector store"}
                
        except Exception as e:
            logger.error(f"Failed to delete knowledge: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        try:
            # This would need to be implemented based on your vector store capabilities
            return {
                "total_documents": 0,  # Would need to query vector store
                "documents_by_type": {},
                "recent_additions": [],
                "top_tags": []
            }
        except Exception as e:
            logger.error(f"Failed to get knowledge stats: {e}")
            return {"error": str(e)}
    
    async def suggest_improvements(self, query: str) -> List[Dict[str, Any]]:
        """Suggest improvements to knowledge base based on search patterns."""
        # This could analyze search patterns and suggest new content
        return []


# Global service instance
knowledge_service = KnowledgeBaseService() 