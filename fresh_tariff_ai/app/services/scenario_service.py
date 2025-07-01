"""
Scenario Analysis Service for TariffAI
Provides intelligent scenario analysis with rule-based logic.
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import pandas as pd

from app.core.database import get_tariff_data
from app.services.ai_service import ai_service

logger = logging.getLogger(__name__)


@dataclass
class ScenarioData:
    """Data structure for scenario analysis."""
    product_description: str = ""
    hts_code: str = ""
    base_value: float = 0.0
    quantity: int = 1
    origin_country: str = ""
    destination_country: str = "United States"
    currency: str = "USD"
    shipping_cost: float = 0.0
    insurance_cost: float = 0.0
    additional_costs: float = 0.0
    trade_agreement: Optional[str] = None
    ad_cvd_applicable: bool = False
    special_programs: List[str] = None
    
    def __post_init__(self):
        if self.special_programs is None:
            self.special_programs = []


class ScenarioAnalysisService:
    """Service for intelligent scenario analysis."""
    
    def __init__(self):
        self.tariff_data = None
        self.scenarios: Dict[str, ScenarioData] = {}
        
    async def initialize(self):
        """Initialize the scenario analysis service."""
        try:
            self.tariff_data = get_tariff_data()
            logger.info("✅ Scenario Analysis Service initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Scenario Analysis Service: {e}")
            raise
    
    async def create_scenario(self, scenario_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new scenario with collected data."""
        try:
            scenario = ScenarioData(
                product_description=data.get("product_description", ""),
                hts_code=data.get("hts_code", ""),
                base_value=float(data.get("base_value", 0)),
                quantity=int(data.get("quantity", 1)),
                origin_country=data.get("origin_country", ""),
                destination_country=data.get("destination_country", "United States"),
                currency=data.get("currency", "USD"),
                shipping_cost=float(data.get("shipping_cost", 0)),
                insurance_cost=float(data.get("insurance_cost", 0)),
                additional_costs=float(data.get("additional_costs", 0))
            )
            
            self.scenarios[scenario_id] = scenario
            
            # Analyze the scenario
            analysis = await self._analyze_scenario(scenario)
            
            return {
                "success": True,
                "scenario_id": scenario_id,
                "data": scenario,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error creating scenario: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _analyze_scenario(self, scenario: ScenarioData) -> Dict[str, Any]:
        """Analyze a scenario using rule-based logic."""
        try:
            analysis = {
                "tariff_rate": 0.0,
                "duty_amount": 0.0,
                "total_cost": 0.0,
                "cost_breakdown": {},
                "recommendations": [],
                "risks": [],
                "opportunities": []
            }
            
            # Get tariff rate from database
            tariff_rate = await self._get_tariff_rate(scenario.hts_code, scenario.origin_country)
            analysis["tariff_rate"] = tariff_rate
            
            # Calculate duty amount
            duty_amount = (scenario.base_value * tariff_rate) / 100
            analysis["duty_amount"] = duty_amount
            
            # Calculate total cost
            total_cost = (
                scenario.base_value +
                duty_amount +
                scenario.shipping_cost +
                scenario.insurance_cost +
                scenario.additional_costs
            )
            analysis["total_cost"] = total_cost
            
            # Cost breakdown
            analysis["cost_breakdown"] = {
                "product_value": scenario.base_value,
                "duty_amount": duty_amount,
                "shipping_cost": scenario.shipping_cost,
                "insurance_cost": scenario.insurance_cost,
                "additional_costs": scenario.additional_costs,
                "total": total_cost
            }
            
            # Generate recommendations
            analysis["recommendations"] = await self._generate_recommendations(scenario, analysis)
            
            # Identify risks
            analysis["risks"] = await self._identify_risks(scenario, analysis)
            
            # Identify opportunities
            analysis["opportunities"] = await self._identify_opportunities(scenario, analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing scenario: {e}")
            return {
                "tariff_rate": 0.0,
                "duty_amount": 0.0,
                "total_cost": 0.0,
                "error": str(e)
            }
    
    async def _get_tariff_rate(self, hts_code: str, origin_country: str) -> float:
        """Get tariff rate for HTS code and origin country."""
        try:
            if self.tariff_data is None or not hts_code:
                return 0.0
            
            # Clean HTS code
            clean_hts = hts_code.replace('.', '').replace('-', '').zfill(10)
            
            # Search for matching HTS code
            matches = self.tariff_data[
                self.tariff_data['hts8'].astype(str).str.contains(clean_hts, na=False)
            ]
            
            if not matches.empty:
                rate = matches.iloc[0].get('mfn_ad_val_rate this is the general tariff rate', 0)
                return float(rate) if pd.notna(rate) else 0.0
            
            # If no exact match, try to find similar products
            if self.tariff_data is not None:
                # Search in description
                desc_matches = self.tariff_data[
                    self.tariff_data['brief_description'].str.lower().str.contains(
                        hts_code.lower(), na=False
                    )
                ]
                
                if not desc_matches.empty:
                    rate = desc_matches.iloc[0].get('mfn_ad_val_rate this is the general tariff rate', 0)
                    return float(rate) if pd.notna(rate) else 0.0
            
            return 0.0
            
        except Exception as e:
            logger.error(f"❌ Error getting tariff rate: {e}")
            return 0.0
    
    async def _generate_recommendations(self, scenario: ScenarioData, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on scenario analysis."""
        recommendations = []
        
        try:
            # High tariff rate recommendations
            if analysis["tariff_rate"] > 10:
                recommendations.append("Consider sourcing from countries with lower tariff rates")
                recommendations.append("Explore trade agreements that may reduce duties")
            
            # High total cost recommendations
            if analysis["total_cost"] > scenario.base_value * 1.5:
                recommendations.append("Consider bulk purchasing to reduce per-unit costs")
                recommendations.append("Explore alternative shipping methods")
            
            # Shipping cost recommendations
            if scenario.shipping_cost > scenario.base_value * 0.2:
                recommendations.append("Consider consolidating shipments to reduce shipping costs")
            
            # Currency recommendations
            if scenario.currency != "USD":
                recommendations.append("Monitor exchange rates for potential cost savings")
            
            # Origin country recommendations
            if scenario.origin_country.lower() in ["china", "russia", "iran", "north korea"]:
                recommendations.append("Be aware of potential trade restrictions and sanctions")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Error generating recommendations: {e}")
            return ["Unable to generate recommendations at this time"]
    
    async def _identify_risks(self, scenario: ScenarioData, analysis: Dict[str, Any]) -> List[str]:
        """Identify potential risks in the scenario."""
        risks = []
        
        try:
            # High tariff risks
            if analysis["tariff_rate"] > 15:
                risks.append("High tariff rate may impact profitability")
            
            # Currency risks
            if scenario.currency != "USD":
                risks.append("Currency fluctuation risk")
            
            # Political risks
            if scenario.origin_country.lower() in ["china", "russia", "iran", "north korea"]:
                risks.append("Political and trade policy risks")
            
            # Cost risks
            if analysis["total_cost"] > scenario.base_value * 2:
                risks.append("High total landed cost may affect competitiveness")
            
            return risks
            
        except Exception as e:
            logger.error(f"❌ Error identifying risks: {e}")
            return ["Unable to assess risks at this time"]
    
    async def _identify_opportunities(self, scenario: ScenarioData, analysis: Dict[str, Any]) -> List[str]:
        """Identify potential opportunities in the scenario."""
        opportunities = []
        
        try:
            # Low tariff opportunities
            if analysis["tariff_rate"] < 5:
                opportunities.append("Low tariff rate provides cost advantage")
            
            # Trade agreement opportunities
            if scenario.origin_country.lower() in ["canada", "mexico"]:
                opportunities.append("USMCA trade agreement may provide benefits")
            
            # Scale opportunities
            if scenario.quantity > 100:
                opportunities.append("Bulk purchasing may qualify for volume discounts")
            
            return opportunities
            
        except Exception as e:
            logger.error(f"❌ Error identifying opportunities: {e}")
            return ["Unable to assess opportunities at this time"]
    
    async def compare_scenarios(self, scenario_ids: List[str]) -> Dict[str, Any]:
        """Compare multiple scenarios."""
        try:
            comparisons = []
            
            for scenario_id in scenario_ids:
                if scenario_id in self.scenarios:
                    scenario = self.scenarios[scenario_id]
                    analysis = await self._analyze_scenario(scenario)
                    
                    comparisons.append({
                        "scenario_id": scenario_id,
                        "data": scenario,
                        "analysis": analysis
                    })
            
            # Sort by total cost
            comparisons.sort(key=lambda x: x["analysis"]["total_cost"])
            
            return {
                "success": True,
                "comparisons": comparisons,
                "best_option": comparisons[0] if comparisons else None,
                "cost_savings": self._calculate_cost_savings(comparisons)
            }
            
        except Exception as e:
            logger.error(f"❌ Error comparing scenarios: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _calculate_cost_savings(self, comparisons: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate potential cost savings between scenarios."""
        if len(comparisons) < 2:
            return {}
        
        best_cost = comparisons[0]["analysis"]["total_cost"]
        savings = {}
        
        for comp in comparisons[1:]:
            scenario_id = comp["scenario_id"]
            current_cost = comp["analysis"]["total_cost"]
            savings[scenario_id] = current_cost - best_cost
        
        return savings
    
    def get_scenario(self, scenario_id: str) -> Optional[ScenarioData]:
        """Get a specific scenario."""
        return self.scenarios.get(scenario_id)
    
    def list_scenarios(self) -> List[str]:
        """List all scenario IDs."""
        return list(self.scenarios.keys())
    
    def delete_scenario(self, scenario_id: str) -> bool:
        """Delete a scenario."""
        if scenario_id in self.scenarios:
            del self.scenarios[scenario_id]
            return True
        return False


# Global instance
scenario_service = ScenarioAnalysisService() 