import httpx
import json
from typing import Dict, Any, List, Optional
from loguru import logger
from app.core.config import settings
import asyncio

class AIService:
    """AI service for Ollama integration"""
    
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def generate_response(self, prompt: str, context: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Generate AI response using Ollama"""
        try:
            # Prepare the full prompt with context
            full_prompt = self._build_prompt(prompt, context)
            
            # Call Ollama API
            response = await self._call_ollama(full_prompt)
            
            return {
                'response': response.get('response', ''),
                'confidence': response.get('confidence', 0.8),
                'model': self.model,
                'prompt_tokens': response.get('prompt_eval_count', 0),
                'response_tokens': response.get('eval_count', 0)
            }
            
        except Exception as e:
            logger.error(f"Failed to generate AI response: {e}")
            return {
                'response': 'I apologize, but I encountered an error while processing your request. Please try again.',
                'confidence': 0.0,
                'model': self.model,
                'error': str(e)
            }
    
    def _build_prompt(self, prompt: str, context: Optional[List[Dict[str, Any]]] = None) -> str:
        """Build the full prompt with context"""
        system_prompt = """You are TariffAI, an intelligent assistant specialized in tariff management, HTS codes, and international trade. You help users with:

1. HTS Code Classification: Help identify appropriate HTS codes for products
2. Tariff Calculations: Calculate tariffs and landed costs
3. Material Analysis: Analyze material compositions and suggest alternatives
4. Scenario Simulation: Compare different sourcing scenarios
5. Trade Compliance: Provide guidance on AD/CVD, trade agreements, etc.

Always provide accurate, helpful responses based on the information available. If you're unsure about something, say so rather than guessing."""

        full_prompt = f"{system_prompt}\n\n"
        
        # Add context if available
        if context:
            full_prompt += "Context Information:\n"
            for item in context:
                if isinstance(item, dict):
                    if 'question' in item and 'answer' in item:
                        full_prompt += f"Q: {item['question']}\nA: {item['answer']}\n\n"
                    elif 'hts_code' in item and 'description' in item:
                        full_prompt += f"HTS Code: {item['hts_code']} - {item['description']}\n"
                    elif 'material_name' in item:
                        full_prompt += f"Material: {item['material_name']} - {item.get('composition', '')}\n"
            
            full_prompt += "\n"
        
        full_prompt += f"User Question: {prompt}\n\nAssistant:"
        
        return full_prompt
    
    async def _call_ollama(self, prompt: str) -> Dict[str, Any]:
        """Call Ollama API"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 1000
                }
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                raise Exception(f"Ollama API returned status {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to call Ollama API: {e}")
            raise
    
    async def classify_product(self, product_description: str) -> Dict[str, Any]:
        """Classify product and suggest HTS codes"""
        try:
            prompt = f"""Based on the following product description, suggest the most appropriate HTS code(s):

Product Description: {product_description}

Please provide:
1. The most likely HTS code (6-10 digits)
2. A brief explanation of why this code fits
3. Alternative HTS codes if applicable
4. Any special considerations or requirements

Format your response as JSON with the following structure:
{{
    "primary_hts_code": "XXXX.XX.XXXX",
    "explanation": "Brief explanation",
    "alternatives": ["XXXX.XX.XXXX", "XXXX.XX.XXXX"],
    "considerations": ["Consideration 1", "Consideration 2"]
}}"""

            response = await self.generate_response(prompt)
            
            # Try to parse JSON response
            try:
                import json
                parsed_response = json.loads(response['response'])
                return {
                    'success': True,
                    'classification': parsed_response,
                    'confidence': response['confidence']
                }
            except json.JSONDecodeError:
                # If JSON parsing fails, return the raw response
                return {
                    'success': False,
                    'response': response['response'],
                    'confidence': response['confidence']
                }
                
        except Exception as e:
            logger.error(f"Failed to classify product: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def analyze_materials(self, material_composition: Dict[str, float]) -> Dict[str, Any]:
        """Analyze material composition and suggest alternatives"""
        try:
            composition_str = ", ".join([f"{material}: {percentage}%" for material, percentage in material_composition.items()])
            
            prompt = f"""Analyze the following material composition and suggest alternatives to reduce tariff impact:

Current Composition: {composition_str}

Please provide:
1. Analysis of current tariff impact
2. Suggested alternative compositions
3. Estimated cost savings
4. Quality considerations
5. Implementation recommendations

Format your response as JSON with the following structure:
{{
    "current_analysis": {{
        "tariff_impact": "High/Medium/Low",
        "estimated_rate": "X%"
    }},
    "alternatives": [
        {{
            "composition": {{"material": "percentage"}},
            "cost_savings": "X%",
            "quality_impact": "Minimal/Moderate/Significant",
            "implementation": "Easy/Moderate/Difficult"
        }}
    ],
    "recommendations": ["Recommendation 1", "Recommendation 2"]
}}"""

            response = await self.generate_response(prompt)
            
            try:
                import json
                parsed_response = json.loads(response['response'])
                return {
                    'success': True,
                    'analysis': parsed_response,
                    'confidence': response['confidence']
                }
            except json.JSONDecodeError:
                return {
                    'success': False,
                    'response': response['response'],
                    'confidence': response['confidence']
                }
                
        except Exception as e:
            logger.error(f"Failed to analyze materials: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def simulate_scenario(self, base_scenario: Dict[str, Any], changes: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate scenario changes and calculate impact"""
        try:
            scenario_str = f"""
Base Scenario:
- HTS Code: {base_scenario.get('hts_code', 'N/A')}
- Country: {base_scenario.get('country', 'N/A')}
- Material Cost: ${base_scenario.get('material_cost', 0)}
- Current Tariff Rate: {base_scenario.get('tariff_rate', 0)}%

Proposed Changes:
{json.dumps(changes, indent=2)}
"""

            prompt = f"""Analyze the following scenario change and calculate the impact:

{scenario_str}

Please provide:
1. New tariff calculations
2. Cost savings/losses
3. Risk assessment
4. Recommendations

Format your response as JSON with the following structure:
{{
    "new_calculation": {{
        "new_tariff_rate": "X%",
        "new_tariff_amount": "$X",
        "new_total_cost": "$X"
    }},
    "impact": {{
        "cost_change": "$X",
        "percentage_change": "X%",
        "savings": true/false
    }},
    "risk_assessment": "Low/Medium/High",
    "recommendations": ["Recommendation 1", "Recommendation 2"]
}}"""

            response = await self.generate_response(prompt)
            
            try:
                import json
                parsed_response = json.loads(response['response'])
                return {
                    'success': True,
                    'simulation': parsed_response,
                    'confidence': response['confidence']
                }
            except json.JSONDecodeError:
                return {
                    'success': False,
                    'response': response['response'],
                    'confidence': response['confidence']
                }
                
        except Exception as e:
            logger.error(f"Failed to simulate scenario: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def check_health(self) -> Dict[str, Any]:
        """Check if Ollama service is healthy"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model.get('name', '') for model in models]
                
                return {
                    'healthy': True,
                    'available_models': model_names,
                    'target_model': self.model,
                    'model_available': self.model in model_names
                }
            else:
                return {
                    'healthy': False,
                    'error': f"Ollama API returned status {response.status_code}"
                }
                
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e)
            }
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose() 