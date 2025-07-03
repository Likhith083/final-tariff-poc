import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import asyncio
from loguru import logger
import os

class ChromaService:
    """ChromaDB service for vector search and semantic similarity"""
    
    def __init__(self):
        self.client = None
        self.collections = {}
        
    async def initialize(self):
        """Initialize ChromaDB client"""
        try:
            # Ensure ChromaDB directory exists
            chroma_path = os.path.join(os.path.dirname(__file__), '../../data/chroma')
            os.makedirs(chroma_path, exist_ok=True)
            
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=chroma_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Initialize collections
            await self._init_collections()
            
            logger.info("ChromaDB service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
    
    async def _init_collections(self):
        """Initialize required collections"""
        try:
            # HTS Codes collection
            self.collections["hts_codes"] = self.client.get_or_create_collection(
                name="hts_codes",
                metadata={"description": "HTS codes and descriptions for tariff lookup"}
            )
            
            logger.info("ChromaDB collections initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize collections: {e}")
            raise
    
    async def get_collection(self, collection_name: str):
        """Get a specific collection"""
        if collection_name not in self.collections:
            raise ValueError(f"Collection '{collection_name}' not found")
        return self.collections[collection_name]
    
    async def search_hts_codes(self, query: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """Search HTS codes by description using vector similarity"""
        try:
            collection = await self.get_collection("hts_codes")
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            if results["metadatas"] and results["metadatas"][0]:
                for i, metadata in enumerate(results["metadatas"][0]):
                    formatted_results.append({
                        "hts_code": metadata.get("hts_code", ""),
                        "description": metadata.get("description", ""),
                        "duty_rate": metadata.get("duty_rate", ""),
                        "category": metadata.get("category", ""),
                        "similarity_score": 1 - results["distances"][0][i] if results["distances"] else 0.0
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search HTS codes: {e}")
            return []
    
    async def get_suggestions(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Get HTS code suggestions for autocomplete"""
        try:
            collection = await self.get_collection("hts_codes")
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["metadatas", "distances"]
            )
            
            # Format suggestions for autocomplete
            formatted_suggestions = []
            if results["metadatas"] and results["metadatas"][0]:
                for i, metadata in enumerate(results["metadatas"][0]):
                    formatted_suggestions.append({
                        'hts_code': metadata.get("hts_code", ""),
                        'description': metadata.get("description", ""),
                        'display_text': f"{metadata.get('hts_code', '')} - {metadata.get('description', '')}",
                        'similarity_score': 1 - results["distances"][0][i] if results["distances"] else 0.0
                    })
            
            return formatted_suggestions
            
        except Exception as e:
            logger.error(f"Failed to get suggestions: {e}")
            return []
    
    async def add_hts_codes(self, hts_data: List[Dict[str, Any]]):
        """Add HTS codes to the collection"""
        try:
            collection = await self.get_collection("hts_codes")
            
            documents = []
            metadatas = []
            ids = []
            
            for hts in hts_data:
                hts_code = hts.get("hts_code", "")
                description = hts.get("description", "")
                
                # Create document content for vector embedding
                content = f"HTS Code: {hts_code}\nDescription: {description}"
                
                documents.append(content)
                metadatas.append({
                    "hts_code": hts_code,
                    "description": description,
                    "duty_rate": hts.get("duty_rate", ""),
                    "category": hts.get("category", ""),
                    "type": "hts_code"
                })
                ids.append(f"hts_{hts_code}")
            
            if documents:
                collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                logger.info(f"Added {len(documents)} HTS codes to ChromaDB")
                
        except Exception as e:
            logger.error(f"Failed to add HTS codes: {e}")
    
    async def reset_collection(self, collection_name: str):
        """Reset a collection"""
        try:
            if collection_name in self.collections:
                self.client.delete_collection(collection_name)
                self.collections.pop(collection_name)
                await self._init_collections()
                logger.info(f"Reset collection: {collection_name}")
        except Exception as e:
            logger.error(f"Failed to reset collection: {e}")
    
    async def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            collection = await self.get_collection(collection_name)
            count = collection.count()
            return {
                "collection_name": collection_name,
                "total_documents": count,
                "status": "active"
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {} 