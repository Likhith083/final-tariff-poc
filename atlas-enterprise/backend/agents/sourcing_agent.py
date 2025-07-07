"""
ATLAS Enterprise - Sourcing Advisor Agent
AI agent for autonomous sourcing recommendations and cost optimization
"""

import json
import logging
from typing import Dict, List, Any, Optional, TypedDict, Annotated
from datetime import datetime
import asyncio

# LangGraph imports
try:
    from langgraph.graph import StateGraph, END
    from langgraph.prebuilt import ToolExecutor, ToolInvocation
    from langchain.tools import Tool
    from langchain.schema import BaseMessage, HumanMessage, AIMessage
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("LangGraph not available - using simplified agent implementation")

# Local imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..main_unified import search_hts_data, calculate_tariff

logger = logging.getLogger(__name__)

class SourcingState(TypedDict):
    """State for the sourcing agent"""
    messages: List[BaseMessage]
    product_description: str
    target_countries: List[str]
    product_value: float
    quantity: int
    hts_candidates: List[Dict]
    country_analysis: Dict[str, Any]
    recommendations: List[Dict]
    reasoning: str
    confidence_score: float

class SourcingAdvisorAgent:
    """
    Intelligent sourcing advisor agent that provides autonomous recommendations
    for optimal sourcing strategies based on tariffs, costs, and risks.
    """
    
    def __init__(self, hts_search_func=None, tariff_calc_func=None):
        self.hts_search_func = hts_search_func
        self.tariff_calc_func = tariff_calc_func
        self.country_data = self._load_country_data()
        
        if LANGGRAPH_AVAILABLE:
            self.graph = self._create_langgraph()
        else:
            self.graph = None
            
    def _load_country_data(self) -> Dict[str, Any]:
        """Load country-specific data for sourcing analysis"""
        return {
            "CN": {
                "name": "China",
                "manufacturing_strength": 0.95,
                "cost_factor": 1.0,
                "lead_time_weeks": 5,
                "risk_level": "high",
                "trade_agreements": [],
                "section_301_affected": True,
                "strengths": ["Low cost", "High capacity", "Advanced manufacturing"],
                "weaknesses": ["High tariffs", "Trade tensions", "Long lead times"]
            },
            "VN": {
                "name": "Vietnam", 
                "manufacturing_strength": 0.75,
                "cost_factor": 1.15,
                "lead_time_weeks": 4,
                "risk_level": "medium",
                "trade_agreements": ["GSP"],
                "section_301_affected": False,
                "strengths": ["GSP benefits", "Growing capacity", "Stable relations"],
                "weaknesses": ["Limited capacity", "Higher costs", "Infrastructure gaps"]
            },
            "MX": {
                "name": "Mexico",
                "manufacturing_strength": 0.70,
                "cost_factor": 1.25,
                "lead_time_weeks": 2,
                "risk_level": "low",
                "trade_agreements": ["USMCA"],
                "section_301_affected": False,
                "strengths": ["USMCA benefits", "Short lead times", "Proximity"],
                "weaknesses": ["Higher costs", "Limited tech capacity", "Security concerns"]
            },
            "IN": {
                "name": "India",
                "manufacturing_strength": 0.80,
                "cost_factor": 1.10,
                "lead_time_weeks": 6,
                "risk_level": "medium",
                "trade_agreements": ["GSP"],
                "section_301_affected": False,
                "strengths": ["Large market", "Tech capabilities", "English speaking"],
                "weaknesses": ["Complex regulations", "Infrastructure", "Quality variance"]
            },
            "TH": {
                "name": "Thailand",
                "manufacturing_strength": 0.65,
                "cost_factor": 1.20,
                "lead_time_weeks": 4,
                "risk_level": "low",
                "trade_agreements": ["GSP"],
                "section_301_affected": False,
                "strengths": ["Political stability", "Good infrastructure", "GSP eligible"],
                "weaknesses": ["Higher costs", "Limited capacity", "Currency risk"]
            }
        }
    
    def _create_langgraph(self) -> StateGraph:
        """Create the LangGraph workflow for sourcing analysis"""
        if not LANGGRAPH_AVAILABLE:
            return None
            
        # Define tools
        tools = [
            Tool(
                name="search_hts_codes",
                description="Search for HTS codes based on product description",
                func=self._search_hts_codes
            ),
            Tool(
                name="calculate_country_costs",
                description="Calculate total costs for each target country",
                func=self._calculate_country_costs
            ),
            Tool(
                name="analyze_risks",
                description="Analyze risks for each sourcing option",
                func=self._analyze_risks
            ),
            Tool(
                name="generate_recommendations",
                description="Generate final sourcing recommendations",
                func=self._generate_recommendations
            )
        ]
        
        tool_executor = ToolExecutor(tools)
        
        # Create workflow
        workflow = StateGraph(SourcingState)
        
        # Add nodes
        workflow.add_node("search_hts", self._search_hts_node)
        workflow.add_node("analyze_countries", self._analyze_countries_node) 
        workflow.add_node("calculate_costs", self._calculate_costs_node)
        workflow.add_node("assess_risks", self._assess_risks_node)
        workflow.add_node("generate_recommendations", self._generate_recommendations_node)
        
        # Add edges
        workflow.set_entry_point("search_hts")
        workflow.add_edge("search_hts", "analyze_countries")
        workflow.add_edge("analyze_countries", "calculate_costs")
        workflow.add_edge("calculate_costs", "assess_risks")
        workflow.add_edge("assess_risks", "generate_recommendations")
        workflow.add_edge("generate_recommendations", END)
        
        return workflow.compile()
    
    async def analyze_sourcing(self, 
                             product_description: str,
                             target_countries: List[str],
                             product_value: float,
                             quantity: int = 1) -> Dict[str, Any]:
        """
        Main entry point for sourcing analysis
        """
        try:
            if self.graph and LANGGRAPH_AVAILABLE:
                # Use LangGraph workflow
                initial_state = SourcingState(
                    messages=[HumanMessage(content=f"Analyze sourcing for: {product_description}")],
                    product_description=product_description,
                    target_countries=target_countries,
                    product_value=product_value,
                    quantity=quantity,
                    hts_candidates=[],
                    country_analysis={},
                    recommendations=[],
                    reasoning="",
                    confidence_score=0.0
                )
                
                result = await self.graph.ainvoke(initial_state)
                return self._format_result(result)
            else:
                # Fallback to simplified analysis
                return await self._simplified_analysis(
                    product_description, target_countries, product_value, quantity
                )
                
        except Exception as e:
            logger.error(f"Sourcing analysis error: {e}")
            return {
                "success": False,
                "error": str(e),
                "recommendations": [],
                "analysis": {}
            }
    
    async def _simplified_analysis(self, product_description: str, target_countries: List[str], 
                                 product_value: float, quantity: int) -> Dict[str, Any]:
        """Simplified analysis when LangGraph is not available"""
        
        # Step 1: Find HTS codes
        hts_candidates = []
        if self.hts_search_func:
            hts_candidates = self.hts_search_func(product_description, limit=3)
        
        if not hts_candidates:
            return {
                "success": False,
                "error": "No matching HTS codes found",
                "recommendations": [],
                "analysis": {}
            }
        
        # Use the best HTS match
        primary_hts = hts_candidates[0]
        
        # Step 2: Analyze each country
        country_analysis = {}
        for country_code in target_countries:
            try:
                country_info = self.country_data.get(country_code, {})
                
                # Calculate costs
                cost_calculation = None
                if self.tariff_calc_func:
                    cost_calculation = self.tariff_calc_func(
                        primary_hts['hts_code'],
                        product_value,
                        country_code,
                        quantity
                    )
                
                # Analyze this country
                analysis = self._analyze_single_country(
                    country_code, country_info, cost_calculation, primary_hts
                )
                
                country_analysis[country_code] = analysis
                
            except Exception as e:
                logger.error(f"Error analyzing {country_code}: {e}")
                country_analysis[country_code] = {
                    "error": str(e),
                    "country_name": self.country_data.get(country_code, {}).get("name", country_code)
                }
        
        # Step 3: Generate recommendations
        recommendations = self._generate_final_recommendations(
            country_analysis, product_description, product_value
        )
        
        return {
            "success": True,
            "product_description": product_description,
            "hts_code": primary_hts['hts_code'],
            "hts_description": primary_hts['description'],
            "analysis_date": datetime.now().isoformat(),
            "countries": country_analysis,
            "recommendations": recommendations,
            "confidence_score": 0.85
        }
    
    def _analyze_single_country(self, country_code: str, country_info: Dict, 
                               cost_calculation: Dict, hts_info: Dict) -> Dict[str, Any]:
        """Analyze a single country option"""
        
        # Base analysis
        analysis = {
            "country_code": country_code,
            "country_name": country_info.get("name", country_code),
            "manufacturing_strength": country_info.get("manufacturing_strength", 0.5),
            "lead_time_weeks": country_info.get("lead_time_weeks", 4),
            "risk_level": country_info.get("risk_level", "medium"),
            "strengths": country_info.get("strengths", []),
            "weaknesses": country_info.get("weaknesses", [])
        }
        
        # Add cost information
        if cost_calculation:
            analysis.update({
                "duty_rate": cost_calculation.get("duty_rate", 0),
                "total_landed_cost": cost_calculation.get("total_landed_cost", 0),
                "duty_amount": cost_calculation.get("duty_amount", 0),
                "cost_breakdown": cost_calculation.get("calculation_breakdown", {})
            })
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(country_code, country_info, hts_info)
        analysis["risk_score"] = risk_score
        
        # Calculate competitiveness score
        competitiveness = self._calculate_competitiveness(analysis)
        analysis["competitiveness_score"] = competitiveness
        
        return analysis
    
    def _calculate_risk_score(self, country_code: str, country_info: Dict, hts_info: Dict) -> float:
        """Calculate risk score for a country (0-1, lower is better)"""
        base_risk = {"low": 0.1, "medium": 0.5, "high": 0.8}.get(
            country_info.get("risk_level", "medium"), 0.5
        )
        
        # Adjust for trade factors
        if country_info.get("section_301_affected", False):
            base_risk += 0.2
        
        if country_info.get("trade_agreements"):
            base_risk -= 0.1
        
        # Lead time risk
        lead_time = country_info.get("lead_time_weeks", 4)
        if lead_time > 6:
            base_risk += 0.1
        elif lead_time < 3:
            base_risk -= 0.1
        
        return min(max(base_risk, 0.0), 1.0)
    
    def _calculate_competitiveness(self, analysis: Dict) -> float:
        """Calculate overall competitiveness score (0-1, higher is better)"""
        cost_score = 0.5  # Default
        if "total_landed_cost" in analysis:
            # Normalize cost (lower cost = higher score)
            cost_score = max(0.1, 1.0 - (analysis["total_landed_cost"] / 2000))
        
        manufacturing_score = analysis.get("manufacturing_strength", 0.5)
        risk_score = 1.0 - analysis.get("risk_score", 0.5)  # Invert risk
        
        # Lead time score (shorter = better)
        lead_time = analysis.get("lead_time_weeks", 4)
        lead_time_score = max(0.1, 1.0 - (lead_time / 10))
        
        # Weighted average
        competitiveness = (
            cost_score * 0.4 +
            manufacturing_score * 0.25 +
            risk_score * 0.25 +
            lead_time_score * 0.1
        )
        
        return round(competitiveness, 2)
    
    def _generate_final_recommendations(self, country_analysis: Dict, 
                                      product_description: str, product_value: float) -> List[Dict]:
        """Generate final sourcing recommendations"""
        
        recommendations = []
        
        # Sort countries by competitiveness
        sorted_countries = sorted(
            [(code, data) for code, data in country_analysis.items() if "error" not in data],
            key=lambda x: x[1].get("competitiveness_score", 0),
            reverse=True
        )
        
        if not sorted_countries:
            return recommendations
        
        # Primary recommendation
        best_country_code, best_analysis = sorted_countries[0]
        recommendations.append({
            "type": "primary",
            "country_code": best_country_code,
            "country_name": best_analysis["country_name"],
            "reasoning": f"Best overall option with {best_analysis['competitiveness_score']:.0%} competitiveness score",
            "total_cost": best_analysis.get("total_landed_cost", 0),
            "key_benefits": best_analysis.get("strengths", [])[:3],
            "confidence": 0.9
        })
        
        # Alternative recommendation
        if len(sorted_countries) > 1:
            alt_country_code, alt_analysis = sorted_countries[1]
            recommendations.append({
                "type": "alternative",
                "country_code": alt_country_code,
                "country_name": alt_analysis["country_name"],
                "reasoning": f"Strong alternative with {alt_analysis['competitiveness_score']:.0%} competitiveness",
                "total_cost": alt_analysis.get("total_landed_cost", 0),
                "key_benefits": alt_analysis.get("strengths", [])[:2],
                "confidence": 0.7
            })
        
        # Risk mitigation recommendation
        low_risk_countries = [
            (code, data) for code, data in sorted_countries
            if data.get("risk_level") == "low"
        ]
        
        if low_risk_countries and low_risk_countries[0][0] != best_country_code:
            risk_country_code, risk_analysis = low_risk_countries[0]
            recommendations.append({
                "type": "risk_mitigation",
                "country_code": risk_country_code,
                "country_name": risk_analysis["country_name"],
                "reasoning": "Lowest risk option for supply chain stability",
                "total_cost": risk_analysis.get("total_landed_cost", 0),
                "key_benefits": ["Low risk", "Stable supply chain"],
                "confidence": 0.8
            })
        
        return recommendations
    
    # LangGraph node functions (used when LangGraph is available)
    async def _search_hts_node(self, state: SourcingState) -> SourcingState:
        """Search for HTS codes"""
        if self.hts_search_func:
            hts_candidates = self.hts_search_func(state["product_description"], limit=3)
            state["hts_candidates"] = hts_candidates
        return state
    
    async def _analyze_countries_node(self, state: SourcingState) -> SourcingState:
        """Analyze target countries"""
        country_analysis = {}
        for country_code in state["target_countries"]:
            country_info = self.country_data.get(country_code, {})
            country_analysis[country_code] = {
                "country_info": country_info,
                "analyzed": True
            }
        state["country_analysis"] = country_analysis
        return state
    
    async def _calculate_costs_node(self, state: SourcingState) -> SourcingState:
        """Calculate costs for each country"""
        if not state["hts_candidates"]:
            return state
            
        primary_hts = state["hts_candidates"][0]
        
        for country_code in state["country_analysis"]:
            if self.tariff_calc_func:
                try:
                    cost_calc = self.tariff_calc_func(
                        primary_hts["hts_code"],
                        state["product_value"],
                        country_code,
                        state["quantity"]
                    )
                    state["country_analysis"][country_code]["cost_calculation"] = cost_calc
                except Exception as e:
                    logger.error(f"Cost calculation error for {country_code}: {e}")
        
        return state
    
    async def _assess_risks_node(self, state: SourcingState) -> SourcingState:
        """Assess risks for each country"""
        for country_code, analysis in state["country_analysis"].items():
            country_info = self.country_data.get(country_code, {})
            hts_info = state["hts_candidates"][0] if state["hts_candidates"] else {}
            
            risk_score = self._calculate_risk_score(country_code, country_info, hts_info)
            analysis["risk_score"] = risk_score
        
        return state
    
    async def _generate_recommendations_node(self, state: SourcingState) -> SourcingState:
        """Generate final recommendations"""
        recommendations = self._generate_final_recommendations(
            state["country_analysis"],
            state["product_description"],
            state["product_value"]
        )
        
        state["recommendations"] = recommendations
        state["confidence_score"] = 0.85
        state["reasoning"] = "Analysis completed using comprehensive multi-factor evaluation"
        
        return state
    
    def _format_result(self, state: SourcingState) -> Dict[str, Any]:
        """Format the final result"""
        return {
            "success": True,
            "product_description": state["product_description"],
            "hts_code": state["hts_candidates"][0]["hts_code"] if state["hts_candidates"] else "",
            "analysis_date": datetime.now().isoformat(),
            "countries": state["country_analysis"],
            "recommendations": state["recommendations"],
            "confidence_score": state["confidence_score"],
            "reasoning": state["reasoning"]
        }
    
    # Tool functions for LangGraph
    def _search_hts_codes(self, query: str) -> str:
        """Tool function to search HTS codes"""
        if self.hts_search_func:
            results = self.hts_search_func(query, limit=3)
            return json.dumps(results)
        return "[]"
    
    def _calculate_country_costs(self, data: str) -> str:
        """Tool function to calculate costs"""
        try:
            params = json.loads(data)
            if self.tariff_calc_func:
                result = self.tariff_calc_func(
                    params["hts_code"],
                    params["product_value"],
                    params["country_code"],
                    params.get("quantity", 1)
                )
                return json.dumps(result)
        except Exception as e:
            logger.error(f"Cost calculation tool error: {e}")
        return "{}"
    
    def _analyze_risks(self, country_code: str) -> str:
        """Tool function to analyze risks"""
        country_info = self.country_data.get(country_code, {})
        risk_analysis = {
            "country_code": country_code,
            "risk_level": country_info.get("risk_level", "medium"),
            "trade_agreements": country_info.get("trade_agreements", []),
            "section_301_affected": country_info.get("section_301_affected", False)
        }
        return json.dumps(risk_analysis)
    
    def _generate_recommendations(self, analysis_data: str) -> str:
        """Tool function to generate recommendations"""
        try:
            data = json.loads(analysis_data)
            recommendations = self._generate_final_recommendations(
                data.get("countries", {}),
                data.get("product_description", ""),
                data.get("product_value", 0)
            )
            return json.dumps(recommendations)
        except Exception as e:
            logger.error(f"Recommendation generation error: {e}")
        return "[]"


# Factory function to create agent with dependencies
def create_sourcing_agent(hts_search_func=None, tariff_calc_func=None) -> SourcingAdvisorAgent:
    """Create a sourcing agent with the required dependencies"""
    return SourcingAdvisorAgent(hts_search_func, tariff_calc_func) 