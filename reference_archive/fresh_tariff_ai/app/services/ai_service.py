"""
Enhanced AI Service for TariffAI
Integrates ChromaDB vector search with Ollama LLM for intelligent responses.
"""

import logging
import json
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path
import aiohttp
import pandas as pd

from app.core.config import settings
from app.core.database import get_tariff_data
from app.services.search_service import SearchService

logger = logging.getLogger(__name__)


class AIService:
    """Enhanced AI service with ChromaDB integration and Ollama LLM."""
    
    def __init__(self):
        self.search_service = None
        self.tariff_data = None
        self.adcvd_faq = None
        self.ollama_url = "http://localhost:11434"
        self.model_name = "llama3.2:3b"  # Updated model name
        
    async def initialize(self):
        """Initialize the AI service with all components."""
        try:
            # Initialize search service
            self.search_service = await SearchService.initialize()
            
            # Load tariff data
            self.tariff_data = get_tariff_data()
            
            # Load AD/CVD FAQ
            await self._load_adcvd_faq()
            
            # Test Ollama connection
            await self._test_ollama_connection()
            
            # Index all data in ChromaDB
            await self._index_knowledge_base()
            
            logger.info("✅ AI Service initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI Service: {e}")
            raise
    
    async def _load_adcvd_faq(self):
        """Load AD/CVD FAQ data."""
        try:
            faq_path = Path(settings.data_dir) / "adcvd_faq.json"
            if faq_path.exists():
                with open(faq_path, 'r', encoding='utf-8') as f:
                    self.adcvd_faq = json.load(f)
                logger.info(f"✅ Loaded AD/CVD FAQ with {len(self.adcvd_faq.get('faqs', []))} questions")
            else:
                logger.warning("⚠️ AD/CVD FAQ file not found, creating sample data")
                self.adcvd_faq = self._create_sample_faq()
        except Exception as e:
            logger.error(f"❌ Error loading AD/CVD FAQ: {e}")
            self.adcvd_faq = self._create_sample_faq()
    
    def _create_sample_faq(self) -> Dict[str, Any]:
        """Create sample AD/CVD FAQ data."""
        return {
            "title": "Antidumping and Countervailing Duties (AD/CVD) FAQ",
            "faqs": [
                {
                    "question": "What is dumping?",
                    "answer": "Dumping occurs when a foreign producer sells a product in the United States at a price below normal value."
                },
                {
                    "question": "What are AD/CVD duties?",
                    "answer": "Antidumping and countervailing duties are intended to offset the value of dumping and/or subsidization."
                }
            ]
        }
    
    async def _test_ollama_connection(self):
        """Test connection to Ollama."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.ollama_url}/api/tags") as response:
                    if response.status == 200:
                        models = await response.json()
                        available_models = [model['name'] for model in models.get('models', [])]
                        logger.info(f"✅ Ollama connected. Available models: {available_models}")
                        
                        # Use llama3.2:3b if available, otherwise use first available model
                        if 'llama3.2:3b' in available_models:
                            self.model_name = 'llama3.2:3b'
                        elif available_models:
                            self.model_name = available_models[0]
                        else:
                            logger.warning("⚠️ No models available in Ollama")
                    else:
                        logger.warning(f"⚠️ Ollama connection failed: {response.status}")
        except Exception as e:
            logger.warning(f"⚠️ Could not connect to Ollama: {e}")
    
    async def _index_knowledge_base(self):
        """Index all knowledge base data in ChromaDB."""
        try:
            if not self.search_service or not self.search_service.collection:
                logger.warning("⚠️ Search service not available for indexing")
                return
            
            # Check if already indexed
            if self.search_service.collection.count() > 0:
                logger.info(f"✅ Knowledge base already indexed with {self.search_service.collection.count()} documents")
                return
            
            documents = []
            metadatas = []
            ids = []
            doc_id = 0
            
            # Index tariff data
            if self.tariff_data is not None:
                for idx, row in self.tariff_data.iterrows():
                    hts_code = str(row.get('hts8', '')).strip()
                    description = str(row.get('brief_description', '')).strip()
                    general_rate = row.get('mfn_ad_val_rate this is the general tariff rate', 0)
                    
                    if hts_code and hts_code != 'nan' and description and description != 'nan':
                        # Create document text
                        doc_text = f"HTS Code: {hts_code}. Product: {description}. General Tariff Rate: {general_rate}%"
                        
                        documents.append(doc_text)
                        metadatas.append({
                            "type": "tariff_data",
                            "hts_code": hts_code,
                            "description": description,
                            "general_rate": float(general_rate) if pd.notna(general_rate) else 0.0,
                            "source": "tariff_database"
                        })
                        ids.append(f"tariff_{doc_id}")
                        doc_id += 1
            
            # Index AD/CVD FAQ
            if self.adcvd_faq:
                for faq in self.adcvd_faq.get('faqs', []):
                    question = faq.get('question', '')
                    answer = faq.get('answer', '')
                    
                    if question and answer:
                        doc_text = f"Question: {question}. Answer: {answer}"
                        
                        documents.append(doc_text)
                        metadatas.append({
                            "type": "adcvd_faq",
                            "question": question,
                            "answer": answer,
                            "source": "adcvd_faq"
                        })
                        ids.append(f"faq_{doc_id}")
                        doc_id += 1
            
            # Add documents to ChromaDB
            if documents:
                self.search_service.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                logger.info(f"✅ Indexed {len(documents)} documents in knowledge base")
            
        except Exception as e:
            logger.error(f"❌ Error indexing knowledge base: {e}")
    
    async def generate_response(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate intelligent response using ChromaDB search and Ollama LLM.
        
        Args:
            query: User query
            context: Optional context information
            
        Returns:
            Dict containing response and metadata
        """
        try:
            # Search knowledge base
            search_results = await self._search_knowledge_base(query)
            
            # Generate response using Ollama
            response = await self._generate_llm_response(query, search_results, context)
            
            return {
                "success": True,
                "response": response,
                "search_results": search_results,
                "sources": self._extract_sources(search_results)
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating response: {e}")
            return {
                "success": False,
                "response": "I'm sorry, I encountered an error processing your request. Please try again.",
                "error": str(e)
            }
    
    async def _search_knowledge_base(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search the knowledge base using ChromaDB."""
        try:
            if not self.search_service or not self.search_service.collection:
                logger.warning("⚠️ Search service not available")
                return []
            
            results = self.search_service.collection.query(
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
            
            logger.info(f"🔍 Found {len(formatted_results)} relevant documents for query: {query}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Error searching knowledge base: {e}")
            return []
    
    async def _generate_llm_response(self, query: str, search_results: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> str:
        """Generate response using Ollama LLM."""
        try:
            # Prepare context from search results
            context_text = self._prepare_context(search_results)
            
            # Create prompt
            prompt = self._create_prompt(query, context_text, context)
            
            # Call Ollama
            response = await self._call_ollama(prompt)
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error generating LLM response: {e}")
            # Fallback to simple response
            return self._generate_fallback_response(query, search_results)
    
    def _prepare_context(self, search_results: List[Dict[str, Any]]) -> str:
        """Prepare context from search results."""
        if not search_results:
            return "No relevant information found in the knowledge base."
        
        context_parts = []
        for result in search_results:
            metadata = result.get("metadata", {})
            doc_type = metadata.get("type", "unknown")
            
            if doc_type == "tariff_data":
                hts_code = metadata.get("hts_code", "")
                description = metadata.get("description", "")
                rate = metadata.get("general_rate", 0)
                context_parts.append(f"Tariff Information: HTS Code {hts_code} - {description} (Rate: {rate}%)")
            
            elif doc_type == "adcvd_faq":
                question = metadata.get("question", "")
                answer = metadata.get("answer", "")
                context_parts.append(f"AD/CVD FAQ: {question} - {answer}")
            
            else:
                context_parts.append(result.get("text", ""))
        
        return "\n\n".join(context_parts)
    
    def _create_prompt(self, query: str, context: str, additional_context: Optional[Dict[str, Any]] = None) -> str:
        """Create a prompt for the LLM."""
        prompt = f"""You are TariffAI, an expert assistant for international trade, customs, and tariff matters. You have access to a comprehensive knowledge base of tariff data and AD/CVD information.

User Query: {query}

Relevant Information from Knowledge Base:
{context}

Additional Context: {additional_context or 'None'}

Please provide a helpful, accurate, and comprehensive response based on the information above. If the information is not sufficient, acknowledge what you know and suggest where the user might find more information.

Response:"""
        
        return prompt
    
    async def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API."""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 1000
                    }
                }
                
                async with session.post(f"{self.ollama_url}/api/generate", json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("response", "I'm sorry, I couldn't generate a response.")
                    else:
                        logger.error(f"❌ Ollama API error: {response.status}")
                        raise Exception(f"Ollama API returned status {response.status}")
                        
        except Exception as e:
            logger.error(f"❌ Error calling Ollama: {e}")
            raise
    
    def _generate_fallback_response(self, query: str, search_results: List[Dict[str, Any]]) -> str:
        """Generate a fallback response when LLM is not available."""
        if not search_results:
            return "I'm sorry, I don't have specific information about that. Please try rephrasing your question or contact a customs specialist."
        
        # Create simple response from search results
        response_parts = ["Based on the available information:"]
        
        for result in search_results:
            metadata = result.get("metadata", {})
            doc_type = metadata.get("type", "unknown")
            
            if doc_type == "tariff_data":
                hts_code = metadata.get("hts_code", "")
                description = metadata.get("description", "")
                rate = metadata.get("general_rate", 0)
                response_parts.append(f"- HTS Code {hts_code}: {description} (Tariff Rate: {rate}%)")
            
            elif doc_type == "adcvd_faq":
                question = metadata.get("question", "")
                answer = metadata.get("answer", "")
                response_parts.append(f"- {question}: {answer}")
        
        return "\n".join(response_parts)
    
    def _extract_sources(self, search_results: List[Dict[str, Any]]) -> List[str]:
        """Extract source information from search results."""
        sources = []
        for result in search_results:
            metadata = result.get("metadata", {})
            doc_type = metadata.get("type", "unknown")
            
            if doc_type == "tariff_data":
                hts_code = metadata.get("hts_code", "")
                sources.append(f"Tariff Database - HTS Code: {hts_code}")
            
            elif doc_type == "adcvd_faq":
                sources.append("AD/CVD FAQ Database")
        
        return list(set(sources))  # Remove duplicates


# Global instance
ai_service = AIService() 