"""
Calculation Agent for TariffAI
Handles tariff calculations and cost analysis.
"""

import logging
from typing import Dict, Any, Optional
import re

logger = logging.getLogger(__name__)


class CalculationAgent:
    """Agent for tariff calculations and cost analysis."""
    
    def __init__(self):
        self.name = "CalculationAgent"
        self.default_tariff_rate = 0.05  # 5% default rate
    
    async def calculate_tariff(self, params: Dict[str, Any], session_id: str = None) -> Dict[str, Any]:
        """
        Calculate tariff costs based on provided parameters.
        
        Args:
            params: Calculation parameters
            session_id: Session ID for context
            
        Returns:
            Dict containing calculation results
        """
        try:
            logger.info(f"🧮 Calculating tariff for params: {params}")
            
            # Extract parameters
            value = params.get("value", 0.0)
            hts_code = params.get("hts_code", "Unknown")
            quantity = params.get("quantity", 1)
            country = params.get("country", "US")
            
            # Get tariff rate (simplified - in real app, this would query the database)
            tariff_rate = self._get_tariff_rate(hts_code, country)
            
            # Calculate costs
            tariff_amount = value * tariff_rate
            total_cost = value + tariff_amount
            
            # Calculate additional costs
            additional_costs = self._calculate_additional_costs(value, quantity)
            
            return {
                "success": True,
                "calculation": {
                    "product_value": value,
                    "tariff_rate": tariff_rate,
                    "tariff_amount": tariff_amount,
                    "additional_costs": additional_costs,
                    "total_cost": total_cost + additional_costs["total"],
                    "breakdown": {
                        "product_value": value,
                        "tariff": tariff_amount,
                        "brokerage": additional_costs["brokerage"],
                        "handling": additional_costs["handling"],
                        "transport": additional_costs["transport"]
                    }
                },
                "parameters": {
                    "hts_code": hts_code,
                    "country": country,
                    "quantity": quantity
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Calculation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "calculation": {}
            }
    
    def _get_tariff_rate(self, hts_code: str, country: str) -> float:
        """
        Get tariff rate for HTS code and country.
        This is a simplified implementation.
        """
        # In a real implementation, this would query the tariff database
        # For now, return default rates based on product type
        
        if hts_code.startswith("61") or hts_code.startswith("62"):
            return 0.16  # Textiles
        elif hts_code.startswith("84") or hts_code.startswith("85"):
            return 0.0   # Electronics
        elif hts_code.startswith("73"):
            return 0.025 # Steel products
        else:
            return self.default_tariff_rate
    
    def _calculate_additional_costs(self, value: float, quantity: int) -> Dict[str, float]:
        """
        Calculate additional import costs.
        """
        # Simplified cost calculation
        brokerage = max(50.0, value * 0.01)  # 1% or $50 minimum
        handling = max(25.0, value * 0.005)  # 0.5% or $25 minimum
        transport = max(100.0, value * 0.02)  # 2% or $100 minimum
        
        return {
            "brokerage": brokerage,
            "handling": handling,
            "transport": transport,
            "total": brokerage + handling + transport
        }
    
    def extract_calculation_params(self, text: str) -> Dict[str, Any]:
        """
        Extract calculation parameters from text.
        """
        params = {}
        
        # Extract monetary values
        money_pattern = r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)'
        money_matches = re.findall(money_pattern, text)
        if money_matches:
            params["value"] = float(money_matches[0].replace(",", ""))
        
        # Extract quantities
        quantity_pattern = r'(\d+)\s*(?:units?|pieces?|items?)'
        quantity_match = re.search(quantity_pattern, text.lower())
        if quantity_match:
            params["quantity"] = int(quantity_match.group(1))
        
        # Extract HTS codes
        hts_pattern = r'\b\d{4}\.\d{2}\.\d{2}\b|\b\d{6}\.\d{2}\b|\b\d{8}\b|\b\d{10}\b'
        hts_match = re.search(hts_pattern, text)
        if hts_match:
            params["hts_code"] = hts_match.group()
        
        return params 