import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import asyncio
from loguru import logger
from app.core.config import settings
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
            os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)
            
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=settings.CHROMA_DB_PATH,
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
            
            # AD/CVD FAQ collection
            self.collections["adcvd_faq"] = self.client.get_or_create_collection(
                name="adcvd_faq",
                metadata={"description": "Antidumping and Countervailing Duties FAQ"}
            )
            
            # Material analysis collection
            self.collections["materials"] = self.client.get_or_create_collection(
                name="materials",
                metadata={"description": "Material compositions and alternatives"}
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
        """Search HTS codes by description"""
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
                        "tariff_rate": metadata.get("tariff_rate", 0.0),
                        "country_origin": metadata.get("country_origin", ""),
                        "similarity_score": 1 - results["distances"][0][i] if results["distances"] else 0.0
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search HTS codes: {e}")
            return []
    
    async def search_adcvd_faq(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search AD/CVD FAQ"""
        try:
            collection = await self.get_collection("adcvd_faq")
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
                        "question": metadata.get("question", ""),
                        "answer": metadata.get("answer", ""),
                        "similarity_score": 1 - results["distances"][0][i] if results["distances"] else 0.0
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search AD/CVD FAQ: {e}")
            return []
    
    async def search_materials(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search material compositions"""
        try:
            collection = await self.get_collection("materials")
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
                        "material_name": metadata.get("material_name", ""),
                        "composition": metadata.get("composition", {}),
                        "tariff_impact": metadata.get("tariff_impact", 0.0),
                        "alternatives": metadata.get("alternatives", []),
                        "similarity_score": 1 - results["distances"][0][i] if results["distances"] else 0.0
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search materials: {e}")
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
                
                # Create document content
                content = f"HTS Code: {hts_code}\nDescription: {description}"
                
                documents.append(content)
                metadatas.append({
                    "hts_code": hts_code,
                    "description": description,
                    "tariff_rate": hts.get("tariff_rate", 0.0),
                    "country_origin": hts.get("country_origin", "US"),
                    "type": "hts_code"
                })
                ids.append(f"hts_{hts_code}")
            
            if documents:
                await collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                logger.info(f"Added {len(documents)} HTS codes to ChromaDB")
                
        except Exception as e:
            logger.error(f"Failed to add HTS codes: {e}")
    
    async def add_materials(self, materials_data: List[Dict[str, Any]]):
        """Add material compositions to the collection"""
        try:
            collection = await self.get_collection("materials")
            
            documents = []
            metadatas = []
            ids = []
            
            for material in materials_data:
                material_name = material.get("name", "")
                composition = material.get("composition", {})
                
                # Create document content
                content = f"Material: {material_name}\nComposition: {composition}"
                
                documents.append(content)
                metadatas.append({
                    "material_name": material_name,
                    "composition": composition,
                    "tariff_impact": material.get("tariff_impact", 0.0),
                    "alternatives": material.get("alternatives", []),
                    "type": "material"
                })
                ids.append(f"material_{material_name}")
            
            if documents:
                await collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                logger.info(f"Added {len(documents)} materials to ChromaDB")
                
        except Exception as e:
            logger.error(f"Failed to add materials: {e}")
    
    async def reset_collection(self, collection_name: str):
        """Reset a specific collection"""
        try:
            if collection_name in self.collections:
                self.client.delete_collection(collection_name)
                await self._init_collections()
                logger.info(f"Collection '{collection_name}' reset successfully")
            else:
                logger.warning(f"Collection '{collection_name}' not found")
                
        except Exception as e:
            logger.error(f"Failed to reset collection '{collection_name}': {e}")
    
    async def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            collection = await self.get_collection(collection_name)
            count = collection.count()
            
            return {
                "collection_name": collection_name,
                "document_count": count,
                "metadata": collection.metadata
            }
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {}
