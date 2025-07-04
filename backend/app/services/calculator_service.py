from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.hts import HTSRecord
from app.services.hts_service import HTSService

class CalculatorService:
    def __init__(self):
        self.hts_service = HTSService()
        
    async def calculate_duty(
        self, 
        hts_code: str, 
        quantity: float, 
        unit_price: float, 
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Calculate duty for given HTS code and values"""
        
        # Validate inputs
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")
        if unit_price <= 0:
            raise ValueError("Unit price must be greater than 0")
        
        # Calculate total value
        total_value = quantity * unit_price
        
        # Get duty rate from HTS code
        duty_rate = await self._get_duty_rate(hts_code, description)
        
        # Calculate duty amount
        duty_amount = total_value * (duty_rate / 100)
        
        # Calculate total with duty
        total_with_duty = total_value + duty_amount
        
        return {
            "hts_code": hts_code,
            "description": description or f"Product with HTS code {hts_code}",
            "quantity": quantity,
            "unit_price": unit_price,
            "total_value": total_value,
            "duty_rate": duty_rate,
            "duty_amount": duty_amount,
            "total_with_duty": total_with_duty,
            "calculation_breakdown": {
                "value_calculation": f"{quantity} × ${unit_price:.2f} = ${total_value:.2f}",
                "duty_calculation": f"${total_value:.2f} × {duty_rate}% = ${duty_amount:.2f}",
                "total_calculation": f"${total_value:.2f} + ${duty_amount:.2f} = ${total_with_duty:.2f}"
            }
        }
    
    async def _get_duty_rate(self, hts_code: str, description: Optional[str] = None) -> float:
        """Get duty rate for HTS code from database or use default"""
        
        # This would typically query the database
        # For now, we'll use a simplified approach
        
        # Default duty rates based on HTS code patterns
        default_rates = {
            "85": 2.5,  # Electrical machinery
            "84": 2.5,  # Machinery
            "90": 2.5,  # Optical instruments
            "39": 3.0,  # Plastics
            "72": 5.0,  # Iron and steel
            "73": 5.0,  # Iron/steel articles
            "87": 2.5,  # Vehicles
            "95": 3.0,  # Toys and games
            "61": 16.0, # Apparel (knitted)
            "62": 16.0, # Apparel (woven)
            "64": 8.5,  # Footwear
            "42": 8.0,  # Leather articles
            "91": 3.0,  # Clocks and watches
            "92": 3.0,  # Musical instruments
        }
        
        # Try to match HTS code prefix
        for prefix, rate in default_rates.items():
            if hts_code.startswith(prefix):
                return rate
        
        # If no match found, use a general rate
        return 3.0
    
    async def calculate_batch_duties(self, items: list) -> Dict[str, Any]:
        """Calculate duties for multiple items"""
        
        results = []
        total_duty = 0
        total_value = 0
        
        for item in items:
            try:
                result = await self.calculate_duty(
                    hts_code=item["hts_code"],
                    quantity=item["quantity"],
                    unit_price=item["unit_price"],
                    description=item.get("description")
                )
                results.append(result)
                total_duty += result["duty_amount"]
                total_value += result["total_value"]
            except Exception as e:
                results.append({
                    "hts_code": item["hts_code"],
                    "error": str(e)
                })
        
        return {
            "items": results,
            "summary": {
                "total_items": len(items),
                "successful_calculations": len([r for r in results if "error" not in r]),
                "total_value": total_value,
                "total_duty": total_duty,
                "total_with_duty": total_value + total_duty,
                "average_duty_rate": (total_duty / total_value * 100) if total_value > 0 else 0
            }
        }
    
    def validate_calculation_inputs(self, hts_code: str, quantity: float, unit_price: float) -> Dict[str, Any]:
        """Validate calculation inputs and return validation results"""
        
        errors = []
        warnings = []
        
        # Validate HTS code
        if not self.hts_service.validate_hts_code(hts_code):
            errors.append("Invalid HTS code format")
        
        # Validate quantity
        if quantity <= 0:
            errors.append("Quantity must be greater than 0")
        elif quantity > 1000000:
            warnings.append("Very large quantity - please verify")
        
        # Validate unit price
        if unit_price <= 0:
            errors.append("Unit price must be greater than 0")
        elif unit_price > 100000:
            warnings.append("Very high unit price - please verify")
        
        # Check for reasonable total value
        total_value = quantity * unit_price
        if total_value > 10000000:
            warnings.append("Very high total value - please verify")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "total_value": total_value
        }
    
    async def get_duty_rate_info(self, hts_code: str) -> Dict[str, Any]:
        """Get detailed information about duty rates for an HTS code"""
        
        # This would typically query the database for detailed rate information
        # For now, return basic information
        
        duty_rate = await self._get_duty_rate(hts_code)
        
        return {
            "hts_code": hts_code,
            "duty_rate": duty_rate,
            "rate_type": "General",  # Could be "Preferential", "General", "Special"
            "effective_date": "2025-01-01",
            "notes": "Standard duty rate",
            "additional_fees": {
                "merchandise_processing_fee": 0.3464,  # Percentage
                "harbor_maintenance_fee": 0.125,  # Percentage
                "customs_bond_fee": 0.0  # Fixed amount
            }
        }
    
    def calculate_additional_fees(self, total_value: float) -> Dict[str, float]:
        """Calculate additional fees beyond basic duty"""
        
        # Merchandise Processing Fee (MPF)
        mpf_rate = 0.3464  # 0.3464%
        mpf_amount = min(total_value * (mpf_rate / 100), 575.00)  # Cap at $575
        
        # Harbor Maintenance Fee (HMF)
        hmf_rate = 0.125  # 0.125%
        hmf_amount = total_value * (hmf_rate / 100)
        
        return {
            "merchandise_processing_fee": mpf_amount,
            "harbor_maintenance_fee": hmf_amount,
            "total_additional_fees": mpf_amount + hmf_amount
        } 