"""
Tariff Calculator Agent - Cost analysis and calculation specialist
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
import re
from forex_python.converter import CurrencyRates

from ..core.config import settings
from ..core.responses import TariffCalculationResponse, ScenarioSimulationResponse

logger = logging.getLogger(__name__)


class TariffCalculatorAgent:
    """
    Tariff Calculation Specialist Agent
    """
    
    def __init__(self):
        self.currency_converter = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize the tariff calculator agent"""
        if self._initialized:
            return
        
        try:
            # Initialize currency converter
            self.currency_converter = CurrencyRates()
            self._initialized = True
            logger.info("✅ Tariff calculator agent initialized successfully")
        except Exception as e:
            logger.error(f"❌ Error initializing tariff calculator: {e}")
            # Continue without currency converter
    
    async def calculate_tariff(self, message: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate tariff and landed cost
        """
        await self.initialize()
        
        try:
            # Extract parameters from message and entities
            params = self._extract_calculation_params(message, entities)
            
            if not params.get("hts_code") or not params.get("material_cost"):
                return {
                    "message": "I need an HTS code and material cost to calculate tariffs. Please provide both.",
                    "data": None
                }
            
            # Perform calculation
            result = await self._perform_calculation(params)
            
            return {
                "message": result["message"],
                "data": result["data"]
            }
            
        except Exception as e:
            logger.error(f"❌ Error in tariff calculation: {e}")
            return {
                "message": "I encountered an error while calculating the tariff. Please check your inputs and try again.",
                "data": None
            }
    
    def _extract_calculation_params(self, message: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Extract calculation parameters from message and entities"""
        params = {}
        
        # Extract HTS code
        if entities.get("hts_codes"):
            params["hts_code"] = entities["hts_codes"][0]
        else:
            # Try to extract from message
            hts_pattern = r'\b\d{4}\.\d{2}\.\d{2}\b'
            hts_matches = re.findall(hts_pattern, message)
            if hts_matches:
                params["hts_code"] = hts_matches[0]
        
        # Extract material cost
        if entities.get("amounts"):
            params["material_cost"] = entities["amounts"][0]
        else:
            # Try to extract from message
            amount_pattern = r'\$\d+(?:\.\d{2})?'
            amount_matches = re.findall(amount_pattern, message)
            if amount_matches:
                params["material_cost"] = float(amount_matches[0].replace('$', ''))
        
        # Extract country
        if entities.get("countries"):
            params["country_of_origin"] = entities["countries"][0]
        else:
            # Default to China if not specified
            params["country_of_origin"] = "China"
        
        # Extract shipping cost (optional)
        shipping_pattern = r'shipping[:\s]*\$?(\d+(?:\.\d{2})?)'
        shipping_match = re.search(shipping_pattern, message.lower())
        if shipping_match:
            params["shipping_cost"] = float(shipping_match.group(1))
        else:
            params["shipping_cost"] = 0.0
        
        return params
    
    async def _perform_calculation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform the actual tariff calculation"""
        hts_code = params["hts_code"]
        material_cost = params["material_cost"]
        country = params["country_of_origin"]
        shipping_cost = params.get("shipping_cost", 0.0)
        
        # Get tariff rate (simplified - in real implementation, this would query the database)
        tariff_rate = await self._get_tariff_rate(hts_code, country)
        
        # Calculate components
        tariff_amount = material_cost * (tariff_rate / 100)
        mpf_amount = material_cost * 0.0021  # Merchandise Processing Fee (0.21%)
        total_landed_cost = material_cost + tariff_amount + shipping_cost + mpf_amount
        
        # Create calculation breakdown
        breakdown = {
            "material_cost": material_cost,
            "tariff_amount": tariff_amount,
            "shipping_cost": shipping_cost,
            "mpf_amount": mpf_amount,
            "total_landed_cost": total_landed_cost
        }
        
        # Format response message
        message = f"Tariff calculation for HTS {hts_code} from {country}:\n"
        message += f"• Material Cost: ${material_cost:.2f}\n"
        message += f"• Tariff Rate: {tariff_rate}%\n"
        message += f"• Tariff Amount: ${tariff_amount:.2f}\n"
        message += f"• Shipping Cost: ${shipping_cost:.2f}\n"
        message += f"• MPF: ${mpf_amount:.2f}\n"
        message += f"• Total Landed Cost: ${total_landed_cost:.2f}"
        
        return {
            "message": message,
            "data": {
                "hts_code": hts_code,
                "hts_description": await self._get_hts_description(hts_code),
                "material_cost": material_cost,
                "tariff_rate": tariff_rate,
                "tariff_amount": tariff_amount,
                "shipping_cost": shipping_cost,
                "mpf_amount": mpf_amount,
                "total_landed_cost": total_landed_cost,
                "country_of_origin": country,
                "currency": "USD",
                "calculation_breakdown": breakdown
            }
        }
    
    async def _get_tariff_rate(self, hts_code: str, country: str) -> float:
        """Get tariff rate for HTS code and country"""
        # Simplified tariff rates - in real implementation, this would query the database
        tariff_rates = {
            "8471.30.01": {"China": 25.0, "Mexico": 0.0, "Canada": 0.0},
            "8517.13.00": {"China": 0.0, "Mexico": 0.0, "Canada": 0.0},
            "9503.00.00": {"China": 0.0, "Mexico": 0.0, "Canada": 0.0},
            "6104.43.20": {"China": 16.0, "Mexico": 0.0, "Canada": 0.0},
            "8528.72.72": {"China": 5.0, "Mexico": 0.0, "Canada": 0.0},
            "4015.19.05": {"China": 3.0, "Mexico": 0.0, "Canada": 0.0},
        }
        
        # Get rate for specific HTS code and country, or use default
        if hts_code in tariff_rates and country in tariff_rates[hts_code]:
            return tariff_rates[hts_code][country]
        elif hts_code in tariff_rates:
            # Use China rate as default
            return tariff_rates[hts_code].get("China", 5.0)
        else:
            # Default tariff rate
            return 5.0
    
    async def _get_hts_description(self, hts_code: str) -> str:
        """Get HTS code description"""
        descriptions = {
            "8471.30.01": "Portable automatic data processing machines",
            "8517.13.00": "Smartphones and mobile phones",
            "9503.00.00": "Other toys and games",
            "6104.43.20": "Women's dresses of synthetic fibers",
            "8528.72.72": "Color television receivers",
            "4015.19.05": "Disposable gloves of vulcanized rubber",
        }
        return descriptions.get(hts_code, "Product classification")
    
    async def simulate_scenario(self, message: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate different scenarios (what-if analysis)
        """
        await self.initialize()
        
        try:
            # Extract scenario parameters
            params = self._extract_scenario_params(message, entities)
            
            if not params.get("hts_code") or not params.get("material_cost"):
                return {
                    "message": "I need an HTS code and material cost to simulate scenarios. Please provide both.",
                    "data": None
                }
            
            # Calculate original scenario
            original_params = {
                "hts_code": params["hts_code"],
                "material_cost": params["material_cost"],
                "country_of_origin": params.get("current_country", "China"),
                "shipping_cost": params.get("shipping_cost", 0.0)
            }
            
            original_result = await self._perform_calculation(original_params)
            
            # Calculate new scenario
            new_params = {
                "hts_code": params["hts_code"],
                "material_cost": params["material_cost"],
                "country_of_origin": params.get("new_country", "Mexico"),
                "shipping_cost": params.get("shipping_cost", 0.0)
            }
            
            new_result = await self._perform_calculation(new_params)
            
            # Calculate differences
            cost_difference = new_result["data"]["total_landed_cost"] - original_result["data"]["total_landed_cost"]
            percentage_change = (cost_difference / original_result["data"]["total_landed_cost"]) * 100
            
            # Create response message
            message = f"Scenario comparison:\n\n"
            message += f"Original (from {original_params['country_of_origin']}): ${original_result['data']['total_landed_cost']:.2f}\n"
            message += f"New (from {new_params['country_of_origin']}): ${new_result['data']['total_landed_cost']:.2f}\n"
            message += f"Difference: ${cost_difference:.2f} ({percentage_change:+.1f}%)"
            
            # Generate recommendations
            recommendations = []
            if cost_difference < 0:
                recommendations.append(f"Sourcing from {new_params['country_of_origin']} would save ${abs(cost_difference):.2f}")
            else:
                recommendations.append(f"Sourcing from {new_params['country_of_origin']} would cost ${cost_difference:.2f} more")
            
            if percentage_change < -10:
                recommendations.append("This represents significant cost savings")
            elif percentage_change > 10:
                recommendations.append("Consider alternative sourcing options")
            
            return {
                "message": message,
                "data": {
                    "original_scenario": original_result["data"],
                    "new_scenario": new_result["data"],
                    "cost_difference": cost_difference,
                    "percentage_change": percentage_change,
                    "recommendations": recommendations
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error in scenario simulation: {e}")
            return {
                "message": "I encountered an error while simulating the scenario. Please check your inputs and try again.",
                "data": None
            }
    
    def _extract_scenario_params(self, message: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Extract scenario parameters from message and entities"""
        params = {}
        
        # Extract HTS code
        if entities.get("hts_codes"):
            params["hts_code"] = entities["hts_codes"][0]
        else:
            hts_pattern = r'\b\d{4}\.\d{2}\.\d{2}\b'
            hts_matches = re.findall(hts_pattern, message)
            if hts_matches:
                params["hts_code"] = hts_matches[0]
        
        # Extract material cost
        if entities.get("amounts"):
            params["material_cost"] = entities["amounts"][0]
        else:
            amount_pattern = r'\$\d+(?:\.\d{2})?'
            amount_matches = re.findall(amount_pattern, message)
            if amount_matches:
                params["material_cost"] = float(amount_matches[0].replace('$', ''))
        
        # Extract countries
        if entities.get("countries"):
            if len(entities["countries"]) >= 2:
                params["current_country"] = entities["countries"][0]
                params["new_country"] = entities["countries"][1]
            else:
                params["current_country"] = entities["countries"][0]
                params["new_country"] = "Mexico"  # Default alternative
        else:
            params["current_country"] = "China"
            params["new_country"] = "Mexico"
        
        return params
    
    async def suggest_alternatives(self, message: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Suggest alternative sourcing countries
        """
        await self.initialize()
        
        try:
            # Extract parameters
            hts_code = None
            if entities.get("hts_codes"):
                hts_code = entities["hts_codes"][0]
            else:
                hts_pattern = r'\b\d{4}\.\d{2}\.\d{2}\b'
                hts_matches = re.findall(hts_pattern, message)
                if hts_matches:
                    hts_code = hts_matches[0]
            
            if not hts_code:
                return {
                    "message": "I need an HTS code to suggest alternative sourcing options. Please provide one.",
                    "data": None
                }
            
            current_country = entities.get("countries", ["China"])[0] if entities.get("countries") else "China"
            
            # Get alternative countries with their tariff rates
            alternatives = await self._get_alternative_countries(hts_code, current_country)
            
            if not alternatives:
                return {
                    "message": f"I couldn't find alternative sourcing options for HTS {hts_code}.",
                    "data": None
                }
            
            # Create response message
            message = f"Alternative sourcing options for HTS {hts_code} (currently from {current_country}):\n\n"
            
            for alt in alternatives:
                savings = alt.get("savings", 0)
                if savings > 0:
                    message += f"• {alt['country']}: {alt['tariff_rate']}% tariff (save ${savings:.2f})\n"
                else:
                    message += f"• {alt['country']}: {alt['tariff_rate']}% tariff (cost ${abs(savings):.2f} more)\n"
            
            # Generate recommendations
            recommendations = []
            best_option = min(alternatives, key=lambda x: x.get("savings", 0))
            if best_option["savings"] > 0:
                recommendations.append(f"Consider sourcing from {best_option['country']} for potential savings")
            else:
                recommendations.append("Current sourcing appears competitive")
            
            return {
                "message": message,
                "data": {
                    "current_country": current_country,
                    "alternatives": alternatives,
                    "recommendations": recommendations
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error in alternative sourcing: {e}")
            return {
                "message": "I encountered an error while finding alternative sourcing options. Please try again.",
                "data": None
            }
    
    async def _get_alternative_countries(self, hts_code: str, current_country: str) -> List[Dict[str, Any]]:
        """Get alternative countries with their tariff rates"""
        # Simplified alternative countries - in real implementation, this would query a database
        alternatives = [
            {"country": "Mexico", "tariff_rate": 0.0, "savings": 25.0},  # Assuming $100 material cost
            {"country": "Canada", "tariff_rate": 0.0, "savings": 25.0},
            {"country": "Vietnam", "tariff_rate": 2.5, "savings": 22.5},
            {"country": "Thailand", "tariff_rate": 3.0, "savings": 22.0},
            {"country": "Germany", "tariff_rate": 2.5, "savings": 22.5},
        ]
        
        # Filter out current country
        alternatives = [alt for alt in alternatives if alt["country"] != current_country]
        
        return alternatives[:5]  # Return top 5 alternatives 