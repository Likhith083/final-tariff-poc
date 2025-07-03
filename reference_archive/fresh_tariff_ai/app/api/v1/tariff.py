"""
Tariff Calculator API endpoints for TariffAI
Provides tariff calculation functionality.
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.responses import create_success_response, create_error_response

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


class TariffCalculationRequest(BaseModel):
    """Tariff calculation request model."""
    hts_code: str = Field(..., description="HTS code")
    value: float = Field(..., description="Product value in USD", gt=0)
    quantity: int = Field(1, description="Quantity", gt=0)
    country: str = Field("US", description="Country of origin")


@router.post("/calculate", response_model=dict)
async def calculate_tariff(request: TariffCalculationRequest):
    """
    Calculate tariff costs for a given HTS code and value.
    """
    try:
        logger.info(f"🧮 Tariff calculation request: {request.hts_code}, ${request.value}")
        
        # Get tariff rate for HTS code
        tariff_rate = get_tariff_rate(request.hts_code, request.country)
        
        # Calculate costs
        tariff_amount = request.value * tariff_rate
        additional_costs = calculate_additional_costs(request.value, request.quantity)
        total_cost = request.value + tariff_amount + additional_costs["total"]
        
        result = {
            "hts_code": request.hts_code,
            "product_value": request.value,
            "tariff_rate": tariff_rate,
            "tariff_amount": tariff_amount,
            "additional_costs": additional_costs,
            "total_cost": total_cost,
            "breakdown": {
                "product_value": request.value,
                "tariff": tariff_amount,
                "brokerage": additional_costs["brokerage"],
                "handling": additional_costs["handling"],
                "transport": additional_costs["transport"]
            }
        }
        
        return create_success_response(
            data={"calculation": result},
            message="Tariff calculation completed successfully"
        )
        
    except Exception as e:
        logger.error(f"❌ Tariff calculation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Calculation failed: {str(e)}"
        )


def get_tariff_rate(hts_code: str, country: str) -> float:
    """
    Get tariff rate for HTS code and country.
    This is a simplified implementation - in production, this would query the database.
    """
    # Simplified tariff rates based on HTS code patterns
    if hts_code.startswith("61") or hts_code.startswith("62"):
        return 0.16  # Textiles
    elif hts_code.startswith("84") or hts_code.startswith("85"):
        return 0.0   # Electronics
    elif hts_code.startswith("73"):
        return 0.025 # Steel products
    elif hts_code.startswith("29"):
        return 0.065 # Chemicals
    elif hts_code.startswith("30"):
        return 0.0   # Pharmaceuticals
    else:
        return 0.05  # Default rate


def calculate_additional_costs(value: float, quantity: int) -> dict:
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