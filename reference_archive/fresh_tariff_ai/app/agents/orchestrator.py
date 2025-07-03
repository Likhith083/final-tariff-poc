"""
Orchestrator Agent for TariffAI
Main coordinator that routes queries to appropriate specialist agents.
"""

import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from app.agents.classification import ClassificationAgent
from app.agents.calculation import CalculationAgent
from app.agents.risk_assessment import RiskAssessmentAgent
from app.services.ai_service import ai_service
from app.core.responses import create_success_response, create_error_response

logger = logging.getLogger(__name__)


@dataclass
class AgentContext:
    """Context for agent coordination."""
    session_id: str
    user_query: str
    intent: Optional[str] = None
    extracted_data: Dict[str, Any] = field(default_factory=dict)
    agent_results: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class OrchestratorAgent:
    """
    Main orchestrator agent that coordinates between specialist agents.
    
    Responsibilities:
    - Intent detection and query classification
    - Agent coordination and result synthesis
    - User session management
    - Final response formatting
    """
    
    def __init__(self):
        self.classification_agent = ClassificationAgent()
        self.calculation_agent = CalculationAgent()
        self.risk_assessment_agent = RiskAssessmentAgent()
        self.sessions: Dict[str, AgentContext] = {}
        self.ai_service = ai_service
        
        # Intent keywords for routing
        self.intent_keywords = {
            "hts_search": [
                "hts code", "tariff code", "classification", "product code",
                "what is the code for", "find code", "search code"
            ],
            "tariff_calculation": [
                "calculate", "cost", "duty", "tariff", "how much",
                "total cost", "landed cost", "import cost"
            ],
            "risk_assessment": [
                "risk", "compliance", "restricted", "prohibited", "license",
                "regulation", "legal", "allowed", "banned"
            ],
            "scenario_analysis": [
                "scenario", "compare", "alternative", "what if", "different",
                "sourcing", "supplier", "country", "option"
            ]
        }
    
    async def process_query(self, query: str, session_id: str = None) -> Dict[str, Any]:
        """
        Process a user query by routing to appropriate agents.
        
        Args:
            query: User's query text
            session_id: Optional session ID for context
            
        Returns:
            Dict containing the processed response
        """
        start_time = time.time()
        
        try:
            # Create or get session context
            if session_id is None:
                session_id = f"session_{int(time.time())}"
            
            context = self._get_or_create_session(session_id, query)
            
            # Detect intent
            intent = self._detect_intent(query)
            context.intent = intent
            
            logger.info(f"🎯 Detected intent: {intent} for session {session_id}")
            
            # Route to appropriate agents
            result = await self._route_to_agents(context)
            
            # Update session
            self.sessions[session_id] = context
            
            # Format response
            response = self._format_response(result, context, time.time() - start_time)
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Orchestrator error: {e}")
            return create_error_response(
                message="Failed to process query",
                error_code="ORCHESTRATOR_ERROR",
                details={"error": str(e)}
            )
    
    def _get_or_create_session(self, session_id: str, query: str) -> AgentContext:
        """Get existing session or create new one."""
        if session_id in self.sessions:
            context = self.sessions[session_id]
            context.user_query = query
            context.timestamp = datetime.now()
            return context
        else:
            return AgentContext(session_id=session_id, user_query=query)
    
    def _detect_intent(self, query: str) -> str:
        """Detect the intent of the user query."""
        query_lower = query.lower()
        
        # Count keyword matches for each intent
        intent_scores = {}
        for intent, keywords in self.intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                intent_scores[intent] = score
        
        # Return the intent with highest score, or default to hts_search
        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        else:
            return "hts_search"  # Default intent
    
    async def _route_to_agents(self, context: AgentContext) -> Dict[str, Any]:
        """Route the query to appropriate agents based on intent."""
        results = {}
        
        try:
            # First, try to use the enhanced AI service for intelligent responses
            if hasattr(self, 'ai_service') and self.ai_service:
                try:
                    ai_result = await self.ai_service.generate_response(
                        query=context.user_query,
                        context={"intent": context.intent, "session_id": context.session_id}
                    )
                    
                    if ai_result.get("success"):
                        results["ai_response"] = ai_result
                        logger.info(f"✅ AI service generated response for intent: {context.intent}")
                        return results
                except Exception as e:
                    logger.warning(f"⚠️ AI service failed, falling back to agents: {e}")
            
            # Fallback to traditional agent routing
            if context.intent == "hts_search":
                # Extract product information
                product_info = self._extract_product_info(context.user_query)
                context.extracted_data["product_info"] = product_info
                
                # Use classification agent
                classification_result = await self.classification_agent.classify_product(
                    product_info.get("description", context.user_query),
                    context.session_id
                )
                results["classification"] = classification_result
                
            elif context.intent == "tariff_calculation":
                # Extract calculation parameters
                calc_params = self._extract_calculation_params(context.user_query)
                context.extracted_data["calculation_params"] = calc_params
                
                # Use calculation agent
                calculation_result = await self.calculation_agent.calculate_tariff(
                    calc_params,
                    context.session_id
                )
                results["calculation"] = calculation_result
                
            elif context.intent == "risk_assessment":
                # Extract HTS code or product info
                hts_code = self._extract_hts_code(context.user_query)
                if not hts_code:
                    product_info = self._extract_product_info(context.user_query)
                    hts_code = product_info.get("hts_code")
                
                context.extracted_data["hts_code"] = hts_code
                
                # Use risk assessment agent
                risk_result = await self.risk_assessment_agent.assess_risk(
                    hts_code,
                    context.session_id
                )
                results["risk_assessment"] = risk_result
                
            elif context.intent == "scenario_analysis":
                # Extract scenario parameters
                scenario_params = self._extract_scenario_params(context.user_query)
                context.extracted_data["scenario_params"] = scenario_params
                
                # Use multiple agents for scenario analysis
                scenario_results = await self._analyze_scenario(scenario_params, context)
                results["scenario_analysis"] = scenario_results
            
            # Store results in context
            context.agent_results = results
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Agent routing error: {e}")
            raise
    
    def _extract_product_info(self, query: str) -> Dict[str, Any]:
        """Extract product information from query."""
        # Simple extraction - can be enhanced with NLP
        info = {
            "description": query,
            "hts_code": None,
            "material": None,
            "origin": None
        }
        
        # Extract HTS code if present
        import re
        hts_match = re.search(r'\b(\d{4}\.\d{2}\.\d{4})\b', query)
        if hts_match:
            info["hts_code"] = hts_match.group(1).replace('.', '')
        
        return info
    
    def _extract_calculation_params(self, query: str) -> Dict[str, Any]:
        """Extract calculation parameters from query."""
        # Simple extraction - can be enhanced
        params = {
            "hts_code": None,
            "material_cost": 0.0,
            "shipping_cost": 0.0,
            "country_of_origin": "China",
            "currency": "USD"
        }
        
        # Extract HTS code
        import re
        hts_match = re.search(r'\b(\d{4}\.\d{2}\.\d{4})\b', query)
        if hts_match:
            params["hts_code"] = hts_match.group(1).replace('.', '')
        
        # Extract costs (simple pattern matching)
        cost_match = re.search(r'\$(\d+(?:,\d+)*(?:\.\d{2})?)', query)
        if cost_match:
            params["material_cost"] = float(cost_match.group(1).replace(',', ''))
        
        return params
    
    def _extract_hts_code(self, query: str) -> Optional[str]:
        """Extract HTS code from query."""
        import re
        hts_match = re.search(r'\b(\d{4}\.\d{2}\.\d{4})\b', query)
        if hts_match:
            return hts_match.group(1).replace('.', '')
        return None
    
    def _extract_scenario_params(self, query: str) -> Dict[str, Any]:
        """Extract scenario analysis parameters."""
        params = {
            "hts_code": None,
            "current_country": "China",
            "alternative_countries": [],
            "material_cost": 0.0
        }
        
        # Extract HTS code
        params["hts_code"] = self._extract_hts_code(query)
        
        return params
    
    async def _analyze_scenario(self, params: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Analyze scenario using multiple agents."""
        results = {}
        
        # Get current scenario
        if params.get("hts_code"):
            current_calc = await self.calculation_agent.calculate_tariff({
                "hts_code": params["hts_code"],
                "material_cost": params.get("material_cost", 1000),
                "country_of_origin": params.get("current_country", "China")
            }, context.session_id)
            results["current_scenario"] = current_calc
        
        # Analyze alternatives
        if params.get("alternative_countries"):
            alternatives = []
            for country in params["alternative_countries"]:
                alt_calc = await self.calculation_agent.calculate_tariff({
                    "hts_code": params["hts_code"],
                    "material_cost": params.get("material_cost", 1000),
                    "country_of_origin": country
                }, context.session_id)
                alternatives.append(alt_calc)
            results["alternatives"] = alternatives
        
        return results
    
    def _format_response(self, results: Dict[str, Any], context: AgentContext, processing_time: float) -> Dict[str, Any]:
        """Format the final response based on agent results."""
        try:
            # Handle AI service responses first
            if "ai_response" in results:
                ai_result = results["ai_response"]
                return create_success_response(
                    data={
                        "response": ai_result.get("response", "I'm sorry, I couldn't generate a response."),
                        "sources": ai_result.get("sources", []),
                        "intent": context.intent
                    },
                    message="AI response generated successfully",
                    session_id=context.session_id,
                    processing_time=processing_time
                )
            
            # Handle traditional agent responses
            if context.intent == "hts_search" and "classification" in results:
                return create_success_response(
                    data=results["classification"],
                    message=f"Found {len(results['classification'].get('data', []))} HTS codes",
                    session_id=context.session_id,
                    processing_time=processing_time
                )
            
            elif context.intent == "tariff_calculation" and "calculation" in results:
                return create_success_response(
                    data=results["calculation"],
                    message="Tariff calculation completed",
                    session_id=context.session_id,
                    processing_time=processing_time
                )
            
            elif context.intent == "risk_assessment" and "risk_assessment" in results:
                return create_success_response(
                    data=results["risk_assessment"],
                    message="Risk assessment completed",
                    session_id=context.session_id,
                    processing_time=processing_time
                )
            
            elif context.intent == "scenario_analysis" and "scenario_analysis" in results:
                return create_success_response(
                    data=results["scenario_analysis"],
                    message="Scenario analysis completed",
                    session_id=context.session_id,
                    processing_time=processing_time
                )
            
            else:
                return create_error_response(
                    message="Unable to process query with current intent",
                    error_code="UNSUPPORTED_INTENT",
                    details={"intent": context.intent}
                )
                
        except Exception as e:
            logger.error(f"❌ Response formatting error: {e}")
            return create_error_response(
                message="Error formatting response",
                error_code="FORMATTING_ERROR",
                details={"error": str(e)}
            )
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a session."""
        if session_id in self.sessions:
            context = self.sessions[session_id]
            return {
                "session_id": context.session_id,
                "intent": context.intent,
                "timestamp": context.timestamp.isoformat(),
                "extracted_data": context.extracted_data,
                "agent_results": context.agent_results
            }
        return None
    
    def clear_session(self, session_id: str) -> bool:
        """Clear a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False 