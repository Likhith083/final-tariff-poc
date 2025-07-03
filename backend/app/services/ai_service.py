import httpx
import json
from typing import Optional, Dict, Any
from app.core.config import settings
from app.services.vector_store import VectorStoreService

class AIService:
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        self.vector_store = VectorStoreService()
        
    async def get_response(self, message: str, session_id: Optional[int] = None) -> str:
        """Get AI response for a user message"""
        
        # Search knowledge base for relevant context
        context = await self._get_relevant_context(message)
        
        # Create context-aware prompt
        system_prompt = self._create_system_prompt()
        
        # Add context to the prompt
        if context:
            enhanced_prompt = f"{system_prompt}\n\nRelevant Information:\n{context}\n\nUser: {message}\n\nAssistant:"
        else:
            enhanced_prompt = f"{system_prompt}\n\nUser: {message}\n\nAssistant:"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": enhanced_prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "max_tokens": 1000
                        }
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "I apologize, but I couldn't generate a response at this time.")
                else:
                    return "I'm experiencing technical difficulties. Please try again later."
                    
        except Exception as e:
            print(f"AI Service Error: {str(e)}")
            return "I'm currently unavailable. Please try again later."
    
    async def _get_relevant_context(self, message: str) -> str:
        """Get relevant context from knowledge base"""
        try:
            results = await self.vector_store.search_knowledge(message, n_results=3)
            if results:
                context_parts = []
                for result in results:
                    if result.get('distance', 1.0) < 0.8:  # Only use relevant results
                        context_parts.append(result['content'])
                
                if context_parts:
                    return "\n\n".join(context_parts)
        except Exception as e:
            print(f"Context retrieval error: {str(e)}")
        
        return ""
    
    def _create_system_prompt(self) -> str:
        """Create system prompt for tariff-related conversations"""
        
        return """You are an expert AI assistant specializing in international trade, customs, and tariff classification. You help users with:

1. HTS (Harmonized Tariff Schedule) code classification
2. Duty rate calculations and explanations
3. Trade compliance questions
4. Import/export regulations
5. Customs documentation requirements
6. Anti-dumping and countervailing duty (AD/CVD) information

Key guidelines:
- Always provide accurate, helpful information based on the provided context
- If you're unsure about specific HTS codes, suggest consulting official sources
- Explain complex trade concepts in simple terms
- Be professional but friendly
- Ask clarifying questions when needed
- Provide practical advice for trade operations
- Reference specific regulations and procedures when applicable

Remember: Your responses should be informative, accurate, and actionable for trade professionals."""
    
    async def classify_product(self, description: str) -> Dict[str, Any]:
        """Classify a product and suggest HTS codes"""
        
        prompt = f"""Based on the following product description, suggest the most appropriate HTS code and provide a brief explanation:

Product: {description}

Please provide:
1. Suggested HTS code (6-10 digits)
2. Brief explanation of classification
3. General duty rate range (if known)
4. Any special considerations

Format your response as JSON:
{{
    "hts_code": "code",
    "explanation": "explanation",
    "duty_rate_range": "range",
    "considerations": "considerations"
}}"""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.3,
                            "max_tokens": 500
                        }
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    response_text = result.get("response", "")
                    
                    # Try to parse JSON response
                    try:
                        return json.loads(response_text)
                    except json.JSONDecodeError:
                        return {
                            "hts_code": "Unknown",
                            "explanation": response_text,
                            "duty_rate_range": "Unknown",
                            "considerations": "Please consult official HTS resources"
                        }
                else:
                    return {
                        "hts_code": "Unknown",
                        "explanation": "Unable to classify at this time",
                        "duty_rate_range": "Unknown",
                        "considerations": "Please consult official HTS resources"
                    }
                    
        except Exception as e:
            print(f"Classification Error: {str(e)}")
            return {
                "hts_code": "Unknown",
                "explanation": "Classification service unavailable",
                "duty_rate_range": "Unknown",
                "considerations": "Please consult official HTS resources"
            }
    
    async def explain_duty_calculation(self, hts_code: str, duty_rate: float, value: float) -> str:
        """Explain duty calculation for educational purposes"""
        
        prompt = f"""Explain how duty is calculated for the following:

HTS Code: {hts_code}
Duty Rate: {duty_rate}%
Value: ${value:,.2f}

Please explain:
1. How the duty amount is calculated
2. What factors might affect the duty rate
3. Any special considerations for this HTS code
4. Tips for accurate valuation

Keep the explanation clear and educational."""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.5,
                            "max_tokens": 800
                        }
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "Unable to provide explanation at this time.")
                else:
                    return "Explanation service is currently unavailable."
                    
        except Exception as e:
            print(f"Explanation Error: {str(e)}")
            return "Explanation service is currently unavailable." 