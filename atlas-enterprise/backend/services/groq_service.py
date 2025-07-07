"""
GroqService for ATLAS Enterprise
Real Groq API implementation for production use.
"""

import os
import json
import asyncio
import httpx
from typing import Dict, List, Any, Optional
from enum import Enum


class GroqModelType(Enum):
    """Enum for different Groq model types."""
    CHAT = "chat"
    ANALYSIS = "analysis"
    FAST = "fast"


class GroqService:
    """Production service for Groq API operations."""
    
    def __init__(self):
        """Initialize GroqService."""
        self.client = None
        self._initialized = False
        self.api_key = os.getenv('GROQ_API_KEY')
        self.base_url = "https://api.groq.com/openai/v1"
        self.models = {
            GroqModelType.CHAT: os.getenv('GROQ_CHAT_MODEL', 'llama3-70b-8192'),
            GroqModelType.ANALYSIS: os.getenv('GROQ_ANALYSIS_MODEL', 'mixtral-8x7b-32768'),
            GroqModelType.FAST: os.getenv('GROQ_FAST_MODEL', 'llama3-8b-8192')
        }
    
    async def initialize(self):
        """Initialize Groq client."""
        if self._initialized:
            return
        
        try:
            if not self.api_key:
                raise ValueError("Groq API key not configured")
            
            # Initialize HTTP client
            self.client = httpx.AsyncClient(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=30.0
            )
            
            # Test connection
            await self._test_connection()
            self._initialized = True
            print("✅ GroqService initialized successfully with real API")
            
        except Exception as e:
            print(f"❌ Failed to initialize GroqService: {e}")
            raise
    
    async def _test_connection(self):
        """Test connection to Groq API."""
        try:
            response = await self.client.get(f"{self.base_url}/models")
            if response.status_code != 200:
                raise Exception(f"API test failed with status {response.status_code}")
        except Exception as e:
            raise Exception(f"Failed to connect to Groq API: {e}")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model_type: GroqModelType = GroqModelType.CHAT,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Create a chat completion using Groq API.
        """
        await self.initialize()
        
        try:
            payload = {
                "model": self.models[model_type],
                "messages": messages,
                "temperature": temperature,
                "stream": stream
            }
            
            if max_tokens:
                payload["max_tokens"] = max_tokens
            
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"API request failed with status {response.status_code}: {response.text}")
            
            result = response.json()
            
            return {
                "content": result["choices"][0]["message"]["content"],
                "model": result["model"],
                "usage": result.get("usage", {})
            }
            
        except Exception as e:
            print(f"❌ Error in chat completion: {e}")
            raise
    
    async def analyze_text(
        self,
        text: str,
        analysis_type: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze text using the analysis model.
        """
        await self.initialize()
        
        prompt = f"""Analyze the following text for {analysis_type}:

Text: {text}

{f'Context: {context}' if context else ''}

Please provide a detailed analysis."""

        messages = [{"role": "user", "content": prompt}]
        
        try:
            result = await self.chat_completion(
                messages=messages,
                model_type=GroqModelType.ANALYSIS,
                temperature=0.1
            )
            
            return {
                "analysis": result["content"],
                "analysis_type": analysis_type,
                "model": result["model"],
                "usage": result["usage"]
            }
            
        except Exception as e:
            print(f"❌ Error in text analysis: {e}")
            raise
    
    async def quick_response(
        self,
        prompt: str,
        context: Optional[str] = None
    ) -> str:
        """
        Get a quick response using the fast model.
        """
        await self.initialize()
        
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        messages = [{"role": "user", "content": full_prompt}]
        
        try:
            result = await self.chat_completion(
                messages=messages,
                model_type=GroqModelType.FAST,
                temperature=0.1,
                max_tokens=150
            )
            
            return result["content"]
            
        except Exception as e:
            print(f"❌ Error in quick response: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check Groq API health.
        """
        try:
            await self.initialize()
            
            # Test with a simple request
            test_messages = [{"role": "user", "content": "Hello, respond with 'API is working'"}]
            result = await self.chat_completion(
                messages=test_messages,
                model_type=GroqModelType.FAST,
                temperature=0.1,
                max_tokens=10
            )
            
            return {
                "status": "healthy",
                "api_accessible": True,
                "test_response": result["content"],
                "model": result["model"]
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "api_accessible": False,
                "error": str(e)
            }
    
    async def close(self):
        """Close the HTTP client."""
        if self.client:
            await self.client.aclose()


# Global instance
groq_service = GroqService() 