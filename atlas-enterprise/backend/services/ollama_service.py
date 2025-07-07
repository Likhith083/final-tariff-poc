"""
OllamaService for ATLAS Enterprise
Integration with local Ollama models and knowledge base.
"""

import asyncio
import json
import os
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime

from core.config import settings
from core.logging import get_logger, log_business_event
from services.vector_service import vector_service

logger = get_logger(__name__)


class OllamaService:
    """Service for Ollama local LLM integration with knowledge base."""
    
    def __init__(self):
        """Initialize OllamaService."""
        self.base_url = "http://localhost:11434"
        self._initialized = False
        self.available_models = []
    
    async def initialize(self):
        """Initialize Ollama service and get available models."""
        if self._initialized:
            return
        
        try:
            # Check if Ollama is running
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.available_models = [model["name"] for model in data.get("models", [])]
                self._initialized = True
                logger.info(f"OllamaService initialized with {len(self.available_models)} models: {self.available_models}")
            else:
                raise Exception(f"Ollama API returned status {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to initialize OllamaService: {e}")
            self._initialized = False
            raise
    
    async def get_available_models(self) -> List[str]:
        """Get list of available Ollama models."""
        await self.initialize()
        return self.available_models
    
    async def chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a chat completion using Ollama with knowledge base context.
        
        Args:
            model: Ollama model name
            messages: List of chat messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            context: Additional context from knowledge base
            
        Returns:
            Chat completion response
        """
        await self.initialize()
        
        try:
            # Prepare the prompt with knowledge base context
            system_prompt = self._create_system_prompt(context)
            
            # Format messages for Ollama
            formatted_messages = self._format_messages_for_ollama(messages, system_prompt)
            
            # Prepare request payload
            payload = {
                "model": model,
                "messages": formatted_messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens or 1000
                }
            }
            
            # Make request to Ollama
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=120
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
            
            result = response.json()
            
            # Log business event
            log_business_event(
                "ollama_chat_completion",
                details={
                    "model": model,
                    "message_count": len(messages),
                    "has_context": bool(context),
                    "response_length": len(result.get("message", {}).get("content", ""))
                }
            )
            
            return {
                "content": result.get("message", {}).get("content", ""),
                "model": model,
                "usage": {
                    "prompt_tokens": result.get("prompt_eval_count", 0),
                    "completion_tokens": result.get("eval_count", 0),
                    "total_tokens": result.get("prompt_eval_count", 0) + result.get("eval_count", 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in Ollama chat completion: {e}")
            raise
    
    async def chat_with_knowledge_base(
        self,
        model: str,
        messages: List[Dict[str, str]],
        query: str,
        top_k: int = 5,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Chat with Ollama using knowledge base context from ChromaDB.
        
        Args:
            model: Ollama model name
            messages: List of chat messages
            query: User query for knowledge base search
            top_k: Number of relevant documents to retrieve
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Chat completion with knowledge base context
        """
        try:
            # Search knowledge base for relevant context
            await vector_service.initialize()
            search_results = await vector_service.similarity_search(
                query=query,
                top_k=top_k,
                include_metadata=True
            )
            
            # Build context from search results
            context = self._build_context_from_search_results(search_results)
            
            # Perform chat completion with context
            result = await self.chat_completion(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                context=context
            )
            
            # Add search results to response
            result["knowledge_base_results"] = search_results
            result["context_used"] = bool(context)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in Ollama chat with knowledge base: {e}")
            raise
    
    def _create_system_prompt(self, context: Optional[str] = None) -> str:
        """Create system prompt with knowledge base context."""
        base_prompt = """You are an expert AI assistant for ATLAS Enterprise, a tariff management and trade intelligence platform. You help users with:

- HTS code classification and analysis
- Tariff calculations and duty estimates  
- Trade compliance questions
- Sourcing optimization
- Regulatory guidance
- Import/export documentation

Provide accurate, helpful responses based on trade regulations and best practices."""
        
        if context:
            base_prompt += f"\n\nUse the following knowledge base information to help answer the user's question:\n\n{context}\n\n"
        
        base_prompt += "\nAlways cite sources when possible and provide actionable advice."
        
        return base_prompt
    
    def _format_messages_for_ollama(
        self, 
        messages: List[Dict[str, str]], 
        system_prompt: str
    ) -> List[Dict[str, str]]:
        """Format messages for Ollama API."""
        formatted_messages = []
        
        # Add system message
        formatted_messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # Add user/assistant messages
        for message in messages:
            formatted_messages.append({
                "role": message["role"],
                "content": message["content"]
            })
        
        return formatted_messages
    
    def _build_context_from_search_results(self, search_results: List[Dict[str, Any]]) -> str:
        """Build context string from knowledge base search results."""
        if not search_results:
            return ""
        
        context_parts = []
        for i, result in enumerate(search_results, 1):
            content = result.get("content", "")
            metadata = result.get("metadata", {})
            
            # Add source information if available
            source = metadata.get("source", "Knowledge Base")
            context_parts.append(f"Source {i} ({source}):\n{content}\n")
        
        return "\n".join(context_parts)
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Ollama service health."""
        try:
            await self.initialize()
            
            # Test with a simple model check
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            
            return {
                "status": "healthy",
                "api_accessible": response.status_code == 200,
                "available_models": self.available_models,
                "model_count": len(self.available_models)
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "api_accessible": False,
                "error": str(e),
                "available_models": [],
                "model_count": 0
            }


# Global instance
ollama_service = OllamaService() 