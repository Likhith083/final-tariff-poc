"""
Classification Agent - HTS code expert for product classification and search
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
import chromadb
from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np

from ..core.config import settings
from ..core.responses import HTSCodeResponse

logger = logging.getLogger(__name__)


class ClassificationAgent:
    """
    HTS Classification Specialist Agent
    """
    
    def __init__(self):
        self.embedding_model = None
        self.chroma_client = None
        self.chroma_collection = None
        self.tariff_data = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize the classification agent"""
        if self._initialized:
            return
        
        try:
            # Initialize embedding model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("✅ Embedding model initialized")
            
            # Initialize ChromaDB
            self.chroma_client = chromadb.PersistentClient(path=settings.chroma_db_path)
            collection_name = "hts_search"
            
            try:
                self.chroma_collection = self.chroma_client.get_collection(name=collection_name)
                logger.info(f"✅ Loaded existing ChromaDB collection: {collection_name}")
            except:
                self.chroma_collection = self.chroma_client.create_collection(name=collection_name)
                logger.info(f"✅ Created new ChromaDB collection: {collection_name}")
            
            # Load tariff data
            await self._load_tariff_data()
            
            # Index data if collection is empty
            if self.chroma_collection.count() == 0:
                await self._index_tariff_data()
            
            self._initialized = True
            logger.info("✅ Classification agent initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Error initializing classification agent: {e}")
            raise
    
    async def _load_tariff_data(self):
        """Load tariff data from Excel file"""
        try:
            if settings.tariff_data_path and pd.io.common.file_exists(settings.tariff_data_path):
                self.tariff_data = pd.read_excel(settings.tariff_data_path)
                logger.info(f"✅ Loaded tariff data: {len(self.tariff_data)} records")
            else:
                # Create sample data if file doesn't exist
                self.tariff_data = self._create_sample_data()
                logger.info("⚠️ Created sample tariff data")
        except Exception as e:
            logger.error(f"❌ Error loading tariff data: {e}")
            self.tariff_data = self._create_sample_data()
    
    def _create_sample_data(self) -> pd.DataFrame:
        """Create sample tariff data"""
        sample_data = {
            'hts8': [
                '8471.30.01', '8517.13.00', '9503.00.00', '6104.43.20', '8528.72.72',
                '4015.19.05', '7326.90.86', '3926.90.98', '8543.70.96', '7604.29.50'
            ],
            'brief_description': [
                'Portable automatic data processing machines',
                'Smartphones and mobile phones',
                'Other toys and games',
                "Women's dresses of synthetic fibers",
                'Color television receivers',
                'Disposable gloves of vulcanized rubber',
                'Steel pipes and tubes',
                'Plastic articles for household use',
                'Electronic integrated circuits',
                'Aluminum bars and rods'
            ],
            'mfn_ad_val_rate this is the general tariff rate': [
                0.0, 0.0, 0.0, 16.0, 5.0, 3.0, 2.9, 5.3, 2.6, 2.1
            ]
        }
        return pd.DataFrame(sample_data)
    
    async def _index_tariff_data(self):
        """Index tariff data in ChromaDB"""
        if self.tariff_data is None:
            return
        
        try:
            documents = []
            metadatas = []
            ids = []
            
            for idx, row in self.tariff_data.iterrows():
                hts_code = str(row.get('hts8', '')).strip()
                description = str(row.get('brief_description', '')).strip()
                
                if hts_code and hts_code != 'nan' and description and description != 'nan':
                    # Create document text
                    doc_text = f"HTS Code: {hts_code}. Description: {description}"
                    
                    documents.append(doc_text)
                    metadatas.append({
                        "hts_code": hts_code,
                        "description": description,
                        "tariff_rate": float(row.get('mfn_ad_val_rate this is the general tariff rate', 0)),
                    })
                    ids.append(f"doc_{idx}")
            
            # Add documents in batches
            batch_size = 100
            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i:i + batch_size]
                batch_metadatas = metadatas[i:i + batch_size]
                batch_ids = ids[i:i + batch_size]
                
                self.chroma_collection.add(
                    documents=batch_docs,
                    metadatas=batch_metadatas,
                    ids=batch_ids
                )
            
            logger.info(f"✅ Indexed {len(documents)} documents in ChromaDB")
            
        except Exception as e:
            logger.error(f"❌ Error indexing tariff data: {e}")
    
    async def search_hts_codes(self, query: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for HTS codes based on query
        """
        await self.initialize()
        
        try:
            # Use vector search if available
            if self.chroma_collection and self.embedding_model:
                results = await self._vector_search(query)
            else:
                results = await self._text_search(query)
            
            if not results:
                return {
                    "message": "I couldn't find any HTS codes matching your query. Please try a different description.",
                    "data": {"results": []}
                }
            
            # Format results
            formatted_results = []
            for result in results[:5]:  # Limit to top 5 results
                formatted_results.append(HTSCodeResponse(
                    id=result.get("id", 0),
                    code=result["hts_code"],
                    description=result["description"],
                    tariff_rate=result.get("tariff_rate", 0.0),
                    confidence_score=result.get("confidence", 0.0)
                ))
            
            # Create response message
            if len(formatted_results) == 1:
                result = formatted_results[0]
                message = f"I found HTS code {result.code} for '{result.description}' with a tariff rate of {result.tariff_rate}%."
            else:
                message = f"I found {len(formatted_results)} HTS codes that might match your query:"
                for result in formatted_results:
                    message += f"\n• {result.code}: {result.description} ({result.tariff_rate}% tariff)"
            
            return {
                "message": message,
                "data": {
                    "results": [result.dict() for result in formatted_results],
                    "query": query,
                    "total_count": len(formatted_results)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error in HTS search: {e}")
            return {
                "message": "I encountered an error while searching for HTS codes. Please try again.",
                "data": {"results": []}
            }
    
    async def _vector_search(self, query: str) -> List[Dict[str, Any]]:
        """Perform vector search using ChromaDB"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])
            
            # Search in ChromaDB
            results = self.chroma_collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=10
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    "hts_code": results['metadatas'][0][i]["hts_code"],
                    "description": results['metadatas'][0][i]["description"],
                    "tariff_rate": results['metadatas'][0][i]["tariff_rate"],
                    "confidence": 1 - results['distances'][0][i]  # Convert distance to confidence
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Error in vector search: {e}")
            return []
    
    async def _text_search(self, query: str) -> List[Dict[str, Any]]:
        """Perform text-based search as fallback"""
        try:
            if self.tariff_data is None:
                return []
            
            query_lower = query.lower()
            results = []
            
            for idx, row in self.tariff_data.iterrows():
                hts_code = str(row.get('hts8', '')).strip()
                description = str(row.get('brief_description', '')).strip()
                
                if hts_code and hts_code != 'nan' and description and description != 'nan':
                    # Simple text matching
                    if (query_lower in description.lower() or 
                        any(word in description.lower() for word in query_lower.split())):
                        
                        results.append({
                            "hts_code": hts_code,
                            "description": description,
                            "tariff_rate": float(row.get('mfn_ad_val_rate this is the general tariff rate', 0)),
                            "confidence": 0.7  # Default confidence for text search
                        })
            
            return results[:10]  # Limit results
            
        except Exception as e:
            logger.error(f"❌ Error in text search: {e}")
            return []
    
    async def classify_product(self, product_description: str, company_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Classify a product and suggest HTS codes
        """
        await self.initialize()
        
        try:
            # Enhance query with company information
            enhanced_query = product_description
            if company_name:
                enhanced_query = f"{company_name} {product_description}"
            
            # Search for HTS codes
            search_result = await self.search_hts_codes(enhanced_query, {})
            
            if not search_result.get("data", {}).get("results"):
                return {
                    "message": f"I couldn't classify the product '{product_description}'. Please provide more details.",
                    "hts_codes": [],
                    "confidence": 0.0
                }
            
            results = search_result["data"]["results"]
            
            # Return top result
            top_result = results[0]
            
            return {
                "message": f"Based on the description '{product_description}', I suggest HTS code {top_result['code']} for '{top_result['description']}' with {top_result['tariff_rate']}% tariff rate.",
                "hts_codes": results,
                "confidence": top_result.get("confidence_score", 0.0),
                "suggested_hts_code": top_result['code']
            }
            
        except Exception as e:
            logger.error(f"❌ Error in product classification: {e}")
            return {
                "message": "I encountered an error while classifying the product. Please try again.",
                "hts_codes": [],
                "confidence": 0.0
            }
    
    async def validate_hts_code(self, hts_code: str) -> Dict[str, Any]:
        """
        Validate and get information about an HTS code
        """
        await self.initialize()
        
        try:
            if self.tariff_data is None:
                return {
                    "valid": False,
                    "message": "Tariff data not available for validation."
                }
            
            # Search for exact HTS code match
            match = self.tariff_data[self.tariff_data['hts8'] == hts_code]
            
            if match.empty:
                return {
                    "valid": False,
                    "message": f"HTS code {hts_code} not found in the tariff database."
                }
            
            row = match.iloc[0]
            
            return {
                "valid": True,
                "hts_code": hts_code,
                "description": str(row.get('brief_description', '')),
                "tariff_rate": float(row.get('mfn_ad_val_rate this is the general tariff rate', 0)),
                "message": f"HTS code {hts_code} is valid: {row.get('brief_description', '')}"
            }
            
        except Exception as e:
            logger.error(f"❌ Error validating HTS code: {e}")
            return {
                "valid": False,
                "message": "Error validating HTS code."
            } 