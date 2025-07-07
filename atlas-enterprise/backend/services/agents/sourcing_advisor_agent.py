"""
SourcingAdvisorAgent for ATLAS Enterprise
Intelligent sourcing recommendations using LangGraph and trade intelligence.
"""

from typing import Dict, List, Any, Optional, TypedDict
from datetime import datetime
import asyncio
from langgraph.graph import StateGraph, END

from core.config import settings
from core.logging import get_logger, log_business_event
from ..tariff_calculation_engine import TariffCalculationEngine
from ..vector_service import vector_service
from ..groq_service import groq_service, GroqModelType
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)


class SourcingState(TypedDict):
    """State for sourcing advisor workflow."""
    
    # Input
    product_description: str
    hts_code: Optional[str]
    target_countries: List[str]
    product_value: float
    quantity: float
    
    # Analysis results
    hts_analysis: Optional[Dict[str, Any]]
    tariff_calculations: Optional[List[Dict[str, Any]]]
    trade_agreements: Optional[List[Dict[str, Any]]]
    risk_assessment: Optional[Dict[str, Any]]
    market_intelligence: Optional[Dict[str, Any]]
    
    # Recommendations
    sourcing_recommendations: Optional[List[Dict[str, Any]]]
    final_report: Optional[str]
    
    # Metadata
    processing_steps: List[str]
    errors: List[str]


class SourcingAdvisorAgent:
    """AI agent for intelligent sourcing recommendations."""
    
    def __init__(self):
        """Initialize the sourcing advisor agent."""
        self.llm = None
        self.graph = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize the agent with Groq service and workflow graph."""
        if self._initialized:
            return
        
        try:
            # Initialize Groq service
            await groq_service.initialize()
            
            # Build the workflow graph
            self.graph = self._build_workflow_graph()
            
            self._initialized = True
            logger.info("SourcingAdvisorAgent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize SourcingAdvisorAgent: {e}")
            raise
    
    def _build_workflow_graph(self) -> StateGraph:
        """Build the LangGraph workflow for sourcing analysis."""
        
        workflow = StateGraph(SourcingState)
        
        # Add nodes
        workflow.add_node("analyze_hts", self._analyze_hts_code)
        workflow.add_node("calculate_tariffs", self._calculate_tariffs)
        workflow.add_node("assess_trade_agreements", self._assess_trade_agreements)
        workflow.add_node("evaluate_risks", self._evaluate_risks)
        workflow.add_node("gather_market_intelligence", self._gather_market_intelligence)
        workflow.add_node("generate_recommendations", self._generate_recommendations)
        workflow.add_node("create_final_report", self._create_final_report)
        
        # Define the workflow
        workflow.set_entry_point("analyze_hts")
        workflow.add_edge("analyze_hts", "calculate_tariffs")
        workflow.add_edge("calculate_tariffs", "assess_trade_agreements")
        workflow.add_edge("assess_trade_agreements", "evaluate_risks")
        workflow.add_edge("evaluate_risks", "gather_market_intelligence")
        workflow.add_edge("gather_market_intelligence", "generate_recommendations")
        workflow.add_edge("generate_recommendations", "create_final_report")
        workflow.add_edge("create_final_report", END)
        
        return workflow.compile()
    
    async def _analyze_hts_code(self, state: SourcingState) -> SourcingState:
        """Analyze and validate HTS code for the product."""
        try:
            state["processing_steps"].append("Analyzing HTS code")
            
            if not state.get("hts_code"):
                # Use AI to suggest HTS code based on product description
                context = f"Product: {state['product_description']}"
                
                response = await groq_service.analyze_text(
                    text=context,
                    analysis_type="hts_classification",
                    context="Provide the most likely 10-digit HTS code and explain your reasoning."
                )
                
                # Extract HTS code from response (simplified)
                analysis_text = response.get("analysis", "")
                lines = analysis_text.split('\n')
                for line in lines:
                    if any(char.isdigit() for char in line) and len(line.replace('.', '').replace(' ', '')) >= 8:
                        potential_hts = ''.join(filter(str.isdigit, line))[:10]
                        if len(potential_hts) >= 8:
                            state["hts_code"] = potential_hts.zfill(10)
                            break
            
            # Validate HTS code
            if state.get("hts_code"):
                from services.tariff_database_service import TariffDatabaseService
                validation = await TariffDatabaseService.validate_hts_code(state["hts_code"])
                
                state["hts_analysis"] = {
                    "hts_code": state["hts_code"],
                    "validation": validation,
                    "ai_suggested": not state.get("hts_code"),
                    "confidence": 0.8 if validation["is_valid"] else 0.3
                }
            else:
                state["errors"].append("Could not determine valid HTS code")
                state["hts_analysis"] = {"error": "HTS code determination failed"}
            
            return state
            
        except Exception as e:
            logger.error(f"Error in HTS analysis: {e}")
            state["errors"].append(f"HTS analysis failed: {str(e)}")
            return state
    
    async def _calculate_tariffs(self, state: SourcingState) -> SourcingState:
        """Calculate tariffs for all target countries."""
        try:
            state["processing_steps"].append("Calculating tariffs")
            
            if not state.get("hts_code") or not state.get("target_countries"):
                state["errors"].append("Missing HTS code or target countries for tariff calculation")
                return state
            
            # Mock database session (in real implementation, this would be injected)
            # For now, we'll create a simplified calculation
            calculations = []
            
            for country in state["target_countries"]:
                # Simplified calculation - in production, use TariffCalculationEngine
                calculation = {
                    "country_code": country,
                    "hts_code": state["hts_code"],
                    "estimated_duty_rate": 5.0,  # Placeholder
                    "estimated_total_cost": state["product_value"] * 1.1,  # Placeholder
                    "trade_preferences": [],
                    "calculation_confidence": 0.7
                }
                calculations.append(calculation)
            
            state["tariff_calculations"] = calculations
            return state
            
        except Exception as e:
            logger.error(f"Error in tariff calculation: {e}")
            state["errors"].append(f"Tariff calculation failed: {str(e)}")
            return state
    
    async def _assess_trade_agreements(self, state: SourcingState) -> SourcingState:
        """Assess applicable trade agreements and preferences."""
        try:
            state["processing_steps"].append("Assessing trade agreements")
            
            # Use AI to analyze trade agreements
            context = f"""
            Product: {state['product_description']}
            HTS Code: {state.get('hts_code', 'Unknown')}
            Countries: {', '.join(state.get('target_countries', []))}
            """
            
            response = await groq_service.analyze_text(
                text=context,
                analysis_type="trade_agreements",
                context="Analyze trade agreements and preferences for importing to the US."
            )
            
            # Parse trade agreements (simplified)
            trade_agreements = []
            for country in state.get("target_countries", []):
                agreement = {
                    "country": country,
                    "agreements": ["MFN"],  # Placeholder
                    "duty_reduction": 0.0,
                    "eligibility": "unknown",
                    "requirements": [],
                    "ai_analysis": response.get("analysis", "")[:500]  # First 500 chars
                }
                trade_agreements.append(agreement)
            
            state["trade_agreements"] = trade_agreements
            return state
            
        except Exception as e:
            logger.error(f"Error in trade agreement assessment: {e}")
            state["errors"].append(f"Trade agreement assessment failed: {str(e)}")
            return state
    
    async def _evaluate_risks(self, state: SourcingState) -> SourcingState:
        """Evaluate sourcing risks for each country."""
        try:
            state["processing_steps"].append("Evaluating risks")
            
            # Use AI for risk assessment
            context = f"""
            Product: {state['product_description']}
            Countries: {', '.join(state.get('target_countries', []))}
            """
            
            response = await groq_service.analyze_text(
                text=context,
                analysis_type="risk_assessment",
                context="Evaluate sourcing risks including political, trade, logistics, and quality factors."
            )
            
            # Create risk assessment
            risk_assessment = {
                "overall_risk_level": "medium",
                "risk_factors": [
                    "Political stability",
                    "Trade policy changes", 
                    "Logistics complexity",
                    "Quality control"
                ],
                "country_risks": {},
                "ai_analysis": response.get("analysis", ""),
                "risk_score": 0.6  # 0-1 scale
            }
            
            # Add country-specific risks
            for country in state.get("target_countries", []):
                risk_assessment["country_risks"][country] = {
                    "political_risk": 0.3,
                    "trade_risk": 0.4,
                    "logistics_risk": 0.5,
                    "overall_risk": 0.4
                }
            
            state["risk_assessment"] = risk_assessment
            return state
            
        except Exception as e:
            logger.error(f"Error in risk evaluation: {e}")
            state["errors"].append(f"Risk evaluation failed: {str(e)}")
            return state
    
    async def _gather_market_intelligence(self, state: SourcingState) -> SourcingState:
        """Gather market intelligence and supplier information."""
        try:
            state["processing_steps"].append("Gathering market intelligence")
            
            # Search for relevant documents in vector store
            if vector_service._initialized:
                search_results = await vector_service.similarity_search(
                    f"{state['product_description']} sourcing suppliers",
                    top_k=3
                )
                
                market_intelligence = {
                    "supplier_insights": search_results,
                    "market_trends": "AI analysis would go here",
                    "pricing_intelligence": "Market pricing data would go here",
                    "quality_indicators": "Quality metrics would go here"
                }
            else:
                market_intelligence = {
                    "error": "Vector service not available",
                    "fallback_analysis": "Basic market intelligence placeholder"
                }
            
            state["market_intelligence"] = market_intelligence
            return state
            
        except Exception as e:
            logger.error(f"Error gathering market intelligence: {e}")
            state["errors"].append(f"Market intelligence gathering failed: {str(e)}")
            return state
    
    async def _generate_recommendations(self, state: SourcingState) -> SourcingState:
        """Generate sourcing recommendations based on analysis."""
        try:
            state["processing_steps"].append("Generating recommendations")
            
            # Analyze all collected data to generate recommendations
            recommendations = []
            
            if state.get("tariff_calculations"):
                # Sort countries by total cost
                sorted_countries = sorted(
                    state["tariff_calculations"],
                    key=lambda x: x.get("estimated_total_cost", float('inf'))
                )
                
                for i, calc in enumerate(sorted_countries):
                    country = calc["country_code"]
                    risk = state.get("risk_assessment", {}).get("country_risks", {}).get(country, {})
                    
                    recommendation = {
                        "rank": i + 1,
                        "country": country,
                        "total_cost": calc.get("estimated_total_cost", 0),
                        "duty_rate": calc.get("estimated_duty_rate", 0),
                        "risk_score": risk.get("overall_risk", 0.5),
                        "recommendation_score": self._calculate_recommendation_score(calc, risk),
                        "pros": [],
                        "cons": [],
                        "action_items": []
                    }
                    
                    # Add pros/cons based on analysis
                    if calc.get("estimated_duty_rate", 0) < 5:
                        recommendation["pros"].append("Low duty rate")
                    if risk.get("overall_risk", 0.5) < 0.3:
                        recommendation["pros"].append("Low risk profile")
                    
                    recommendations.append(recommendation)
            
            state["sourcing_recommendations"] = recommendations
            return state
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            state["errors"].append(f"Recommendation generation failed: {str(e)}")
            return state
    
    async def _create_final_report(self, state: SourcingState) -> SourcingState:
        """Create comprehensive final report."""
        try:
            state["processing_steps"].append("Creating final report")
            
            # Use AI to create a comprehensive report
            context = f"""
            Product: {state['product_description']}
            HTS Code: {state.get('hts_code', 'TBD')}
            Countries Analyzed: {', '.join(state.get('target_countries', []))}
            
            Analysis Summary:
            - Tariff calculations completed: {'Yes' if state.get('tariff_calculations') else 'No'}
            - Trade agreements assessed: {'Yes' if state.get('trade_agreements') else 'No'}
            - Risk evaluation completed: {'Yes' if state.get('risk_assessment') else 'No'}
            - Market intelligence gathered: {'Yes' if state.get('market_intelligence') else 'No'}
            
            Recommendations: {len(state.get('sourcing_recommendations', []))} options identified
            """
            
            response = await groq_service.chat_completion(
                messages=[
                    {"role": "system", "content": "You are a senior trade analyst creating an executive summary for sourcing recommendations. Create a professional, actionable report based on the analysis."},
                    {"role": "user", "content": context + "\n\nPlease create an executive summary with key findings and recommendations."}
                ],
                model_type=GroqModelType.ANALYSIS
            )
            
            state["final_report"] = response.get("content", "")
            return state
            
        except Exception as e:
            logger.error(f"Error creating final report: {e}")
            state["errors"].append(f"Final report creation failed: {str(e)}")
            return state
    
    def _calculate_recommendation_score(
        self, 
        calculation: Dict[str, Any], 
        risk: Dict[str, Any]
    ) -> float:
        """Calculate recommendation score based on cost and risk."""
        try:
            # Simple scoring algorithm (0-1 scale)
            cost_score = 1.0 - min(calculation.get("estimated_duty_rate", 0) / 20.0, 1.0)
            risk_score = 1.0 - risk.get("overall_risk", 0.5)
            
            # Weighted average
            return (cost_score * 0.6 + risk_score * 0.4)
            
        except Exception:
            return 0.5  # Default score
    
    async def analyze_sourcing_options(
        self,
        product_description: str,
        target_countries: List[str],
        product_value: float,
        quantity: float = 1.0,
        hts_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze sourcing options for a product across multiple countries.
        
        Args:
            product_description: Description of the product
            target_countries: List of countries to analyze
            product_value: Product value for calculations
            quantity: Quantity to import
            hts_code: Optional HTS code (will be determined if not provided)
            
        Returns:
            Comprehensive sourcing analysis and recommendations
        """
        await self.initialize()
        
        try:
            # Initialize state
            initial_state = SourcingState(
                product_description=product_description,
                hts_code=hts_code,
                target_countries=target_countries,
                product_value=product_value,
                quantity=quantity,
                hts_analysis=None,
                tariff_calculations=None,
                trade_agreements=None,
                risk_assessment=None,
                market_intelligence=None,
                sourcing_recommendations=None,
                final_report=None,
                processing_steps=[],
                errors=[]
            )
            
            # Run the workflow
            final_state = await asyncio.to_thread(self.graph.invoke, initial_state)
            
            # Log business event
            log_business_event(
                "sourcing_analysis_completed",
                details={
                    "product": product_description,
                    "countries": target_countries,
                    "recommendations_count": len(final_state.get("sourcing_recommendations", [])),
                    "processing_steps": len(final_state.get("processing_steps", [])),
                    "errors": len(final_state.get("errors", []))
                }
            )
            
            return {
                "success": True,
                "analysis": final_state,
                "recommendations": final_state.get("sourcing_recommendations", []),
                "report": final_state.get("final_report", ""),
                "processing_steps": final_state.get("processing_steps", []),
                "errors": final_state.get("errors", [])
            }
            
        except Exception as e:
            logger.error(f"Error in sourcing analysis: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "SOURCING_ANALYSIS_ERROR"
            }


# Global instance
sourcing_advisor = SourcingAdvisorAgent() 