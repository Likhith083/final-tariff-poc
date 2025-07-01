"""
Search Service for TariffAI
Handles vector search and database queries
"""

import logging
from typing import Dict, Any, List, Optional
import asyncio
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)


class SearchService:
    """Service for handling vector search and database queries"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.chroma_client = None
            self.collection = None
            self._initialized = True
    
    @classmethod
    async def initialize(cls):
        """Initialize the search service"""
        if cls._instance is None:
            cls._instance = cls()
        
        try:
            # Initialize ChromaDB client
            import chromadb
            from chromadb.config import Settings
            
            # Create persistent client
            chroma_path = Path(settings.data_dir) / "chroma"
            chroma_path.mkdir(parents=True, exist_ok=True)
            
            cls._instance.chroma_client = chromadb.PersistentClient(
                path=str(chroma_path),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            collection_name = "tariff_data"
            try:
                cls._instance.collection = cls._instance.chroma_client.get_collection(collection_name)
                logger.info(f"📚 Using existing collection: {collection_name}")
            except:
                cls._instance.collection = cls._instance.chroma_client.create_collection(
                    name=collection_name,
                    metadata={"description": "Tariff classification data"}
                )
                logger.info(f"📚 Created new collection: {collection_name}")
            
            # Initialize with sample data if collection is empty
            await cls._instance._initialize_sample_data()
            
            logger.info("✅ Search Service initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Search Service: {e}")
            raise
    
    async def _initialize_sample_data(self):
        """Initialize collection with sample tariff data"""
        try:
            # Check if collection has data
            count = self.collection.count()
            if count > 0:
                logger.info(f"📊 Collection already has {count} documents")
                return
            
            # Add sample tariff data
            sample_data = [
                {
                    "id": "sample_1",
                    "text": "Cotton t-shirts made of 100% cotton fabric",
                    "metadata": {
                        "hs_code": "6109.10",
                        "description": "Cotton t-shirts",
                        "category": "Textiles"
                    }
                },
                {
                    "id": "sample_2", 
                    "text": "Plastic water bottles made of PET",
                    "metadata": {
                        "hs_code": "3923.30",
                        "description": "Plastic bottles",
                        "category": "Plastics"
                    }
                },
                {
                    "id": "sample_3",
                    "text": "Steel pipes for construction",
                    "metadata": {
                        "hs_code": "7306.30",
                        "description": "Steel pipes",
                        "category": "Metals"
                    }
                }
            ]
            
            # Add documents to collection
            self.collection.add(
                documents=[item["text"] for item in sample_data],
                metadatas=[item["metadata"] for item in sample_data],
                ids=[item["id"] for item in sample_data]
            )
            
            logger.info(f"📝 Added {len(sample_data)} sample documents")
            
        except Exception as e:
            logger.warning(f"⚠️  Could not initialize sample data: {e}")
    
    async def search_tariffs(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for tariff classifications based on query
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of search results
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=limit,
                include=["metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            if results["ids"] and results["ids"][0]:
                for i, doc_id in enumerate(results["ids"][0]):
                    formatted_results.append({
                        "id": doc_id,
                        "text": results["documents"][0][i] if results["documents"] else "",
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results["distances"] else 0.0
                    })
            
            logger.info(f"🔍 Found {len(formatted_results)} results for query: {query}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Error searching tariffs: {e}")
            return []
    
    async def add_tariff_data(self, text: str, metadata: Dict[str, Any], doc_id: str) -> bool:
        """
        Add new tariff data to the collection
        
        Args:
            text: Document text
            metadata: Document metadata
            doc_id: Unique document ID
            
        Returns:
            bool: Success status
        """
        try:
            self.collection.add(
                documents=[text],
                metadatas=[metadata],
                ids=[doc_id]
            )
            logger.info(f"✅ Added tariff data: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding tariff data: {e}")
            return False
    
    @classmethod
    async def cleanup(cls):
        """Cleanup search service resources"""
        if cls._instance:
            cls._instance.chroma_client = None
            cls._instance.collection = None
            logger.info("✅ Search Service cleaned up")


# Global instance
search_service = SearchService() 