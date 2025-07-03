"""
Orchestrator Agent - Master coordinator for all tariff-related queries
"""
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from ..core.config import settings
from ..core.responses import ChatResponse, ErrorResponse
from .classification import ClassificationAgent
from .tariff_calculator import TariffCalculatorAgent
from .material_analyzer import MaterialAnalyzerAgent

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """
    Master coordinator agent that routes queries to appropriate specialist agents
    """
    
    def __init__(self):
        self.classification_agent = ClassificationAgent()
        self.tariff_calculator_agent = TariffCalculatorAgent()
        self.material_analyzer_agent = MaterialAnalyzerAgent()
        self.user_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def process_query(self, message: str, session_id: Optional[str] = None) -> ChatResponse:
        """
        Process user query and route to appropriate agents
        """
        try:
            # Generate session ID if not provided
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # Initialize session if new
            if session_id not in self.user_sessions:
                self.user_sessions[session_id] = {
                    "created_at": datetime.utcnow(),
                    "message_count": 0,
                    "context": {}
                }
            
            self.user_sessions[session_id]["message_count"] += 1
            
            # Analyze intent and extract entities
            intent, entities = await self._analyze_intent(message)
            
            # Route to appropriate agent based on intent
            if intent == "tariff_calculation":
                response = await self._handle_tariff_calculation(message, entities, session_id)
            elif intent == "hts_search":
                response = await self._handle_hts_search(message, entities, session_id)
            elif intent == "material_analysis":
                response = await self._handle_material_analysis(message, entities, session_id)
            elif intent == "scenario_simulation":
                response = await self._handle_scenario_simulation(message, entities, session_id)
            elif intent == "alternative_sourcing":
                response = await self._handle_alternative_sourcing(message, entities, session_id)
            elif intent == "general_inquiry":
                response = await self._handle_general_inquiry(message, entities, session_id)
            else:
                response = await self._handle_unknown_intent(message, session_id)
            
            # Update session context
            self.user_sessions[session_id]["context"].update(entities)
            
            return ChatResponse(
                message=response["message"],
                session_id=session_id,
                suggestions=response.get("suggestions"),
                data=response.get("data")
            )
            
        except Exception as e:
            logger.error(f"Error in orchestrator: {e}")
            return ChatResponse(
                message="I apologize, but I encountered an error processing your request. Please try again or rephrase your question.",
                session_id=session_id or str(uuid.uuid4()),
                success=False
            )
    
    async def _analyze_intent(self, message: str) -> tuple[str, Dict[str, Any]]:
        """
        Analyze user intent and extract entities
        """
        message_lower = message.lower()
        entities = {}
        
        # Intent classification based on keywords
        if any(word in message_lower for word in ["tariff", "duty", "cost", "calculate", "price"]):
            intent = "tariff_calculation"
        elif any(word in message_lower for word in ["hts", "code", "classification", "find", "search"]):
            intent = "hts_search"
        elif any(word in message_lower for word in ["material", "composition", "analyze", "infer"]):
            intent = "material_analysis"
        elif any(word in message_lower for word in ["scenario", "what if", "compare", "alternative"]):
            intent = "scenario_simulation"
        elif any(word in message_lower for word in ["sourcing", "country", "supplier", "alternative"]):
            intent = "alternative_sourcing"
        else:
            intent = "general_inquiry"
        
        # Extract entities
        entities = await self._extract_entities(message)
        
        return intent, entities
    
    async def _extract_entities(self, message: str) -> Dict[str, Any]:
        """
        Extract entities from user message
        """
        entities = {}
        message_lower = message.lower()
        
        # Extract HTS codes (patterns like 1234.56.78)
        import re
        hts_pattern = r'\b\d{4}\.\d{2}\.\d{2}\b'
        hts_codes = re.findall(hts_pattern, message)
        if hts_codes:
            entities["hts_codes"] = hts_codes
        
        # Extract countries
        countries = ["china", "usa", "united states", "mexico", "canada", "germany", "japan", "uk", "france", "italy"]
        found_countries = [country for country in countries if country in message_lower]
        if found_countries:
            entities["countries"] = found_countries
        
        # Extract monetary amounts
        amount_pattern = r'\$\d+(?:\.\d{2})?'
        amounts = re.findall(amount_pattern, message)
        if amounts:
            entities["amounts"] = [float(amt.replace('$', '')) for amt in amounts]
        
        # Extract product descriptions
        product_keywords = ["gloves", "shirt", "phone", "computer", "toy", "drill", "furniture"]
        found_products = [product for product in product_keywords if product in message_lower]
        if found_products:
            entities["products"] = found_products
        
        return entities
    
    async def _handle_tariff_calculation(self, message: str, entities: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Handle tariff calculation requests"""
        try:
            result = await self.tariff_calculator_agent.calculate_tariff(message, entities)
            return {
                "message": result["message"],
                "suggestions": [
                    "Would you like to compare with different countries?",
                    "Should I analyze alternative materials?",
                    "Would you like to see a detailed breakdown?"
                ],
                "data": result.get("data")
            }
        except Exception as e:
            logger.error(f"Error in tariff calculation: {e}")
            return {
                "message": "I couldn't calculate the tariff. Please provide an HTS code and material cost.",
                "suggestions": ["Try providing an HTS code like 8471.30.01"]
            }
    
    async def _handle_hts_search(self, message: str, entities: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Handle HTS code search requests"""
        try:
            result = await self.classification_agent.search_hts_codes(message, entities)
            return {
                "message": result["message"],
                "suggestions": [
                    "Would you like me to calculate tariffs for any of these codes?",
                    "Should I analyze the material composition?",
                    "Would you like alternative sourcing suggestions?"
                ],
                "data": result.get("data")
            }
        except Exception as e:
            logger.error(f"Error in HTS search: {e}")
            return {
                "message": "I couldn't find HTS codes for your query. Please try a different description.",
                "suggestions": ["Try describing the product more specifically"]
            }
    
    async def _handle_material_analysis(self, message: str, entities: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Handle material analysis requests"""
        try:
            result = await self.material_analyzer_agent.analyze_materials(message, entities)
            return {
                "message": result["message"],
                "suggestions": [
                    "Would you like tariff calculations for these materials?",
                    "Should I suggest alternative materials?",
                    "Would you like to see sourcing options?"
                ],
                "data": result.get("data")
            }
        except Exception as e:
            logger.error(f"Error in material analysis: {e}")
            return {
                "message": "I couldn't analyze the materials. Please provide more product details.",
                "suggestions": ["Try including the company name or product specifications"]
            }
    
    async def _handle_scenario_simulation(self, message: str, entities: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Handle scenario simulation requests"""
        try:
            result = await self.tariff_calculator_agent.simulate_scenario(message, entities)
            return {
                "message": result["message"],
                "suggestions": [
                    "Would you like to explore more scenarios?",
                    "Should I analyze the cost breakdown?",
                    "Would you like sourcing recommendations?"
                ],
                "data": result.get("data")
            }
        except Exception as e:
            logger.error(f"Error in scenario simulation: {e}")
            return {
                "message": "I couldn't simulate the scenario. Please provide specific details.",
                "suggestions": ["Try specifying the HTS code, cost, and countries"]
            }
    
    async def _handle_alternative_sourcing(self, message: str, entities: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Handle alternative sourcing requests"""
        try:
            result = await self.tariff_calculator_agent.suggest_alternatives(message, entities)
            return {
                "message": result["message"],
                "suggestions": [
                    "Would you like detailed cost comparisons?",
                    "Should I analyze the trade agreements?",
                    "Would you like to see supplier information?"
                ],
                "data": result.get("data")
            }
        except Exception as e:
            logger.error(f"Error in alternative sourcing: {e}")
            return {
                "message": "I couldn't find alternative sourcing options. Please provide an HTS code.",
                "suggestions": ["Try providing a specific HTS code to analyze"]
            }
    
    async def _handle_general_inquiry(self, message: str, entities: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Handle general inquiries"""
        return {
            "message": "I'm here to help with tariff calculations, HTS code searches, material analysis, and sourcing recommendations. What would you like to know?",
            "suggestions": [
                "Calculate tariffs for a product",
                "Search for HTS codes",
                "Analyze material composition",
                "Compare sourcing scenarios"
            ]
        }
    
    async def _handle_unknown_intent(self, message: str, session_id: str) -> Dict[str, Any]:
        """Handle unknown or unclear intents"""
        return {
            "message": "I'm not sure what you're asking about. I can help with tariff calculations, HTS code searches, material analysis, and sourcing recommendations. Could you please be more specific?",
            "suggestions": [
                "Try asking about a specific product",
                "Provide an HTS code for analysis",
                "Ask about tariff calculations",
                "Request material composition analysis"
            ]
        }
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information"""
        return self.user_sessions.get(session_id)
    
    def clear_session(self, session_id: str) -> bool:
        """Clear a user session"""
        if session_id in self.user_sessions:
            del self.user_sessions[session_id]
            return True
        return False 