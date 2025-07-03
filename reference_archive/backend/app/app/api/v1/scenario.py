"""
Enhanced Scenario Analysis API endpoints for TariffAI
Provides intelligent scenario analysis with detailed data collection.
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.scenario_service import scenario_service
from app.core.responses import create_success_response, create_error_response

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


class ScenarioDataRequest(BaseModel):
    """Scenario data collection request model."""
    product_description: str = Field(..., description="Product description", min_length=1, max_length=500)
    hts_code: Optional[str] = Field(None, description="HTS code (if known)")
    base_value: float = Field(..., description="Base product value", gt=0)
    quantity: int = Field(1, description="Quantity", gt=0)
    origin_country: str = Field(..., description="Country of origin", min_length=2, max_length=50)
    destination_country: str = Field("United States", description="Destination country")
    currency: str = Field("USD", description="Currency code")
    shipping_cost: float = Field(0.0, description="Shipping cost")
    insurance_cost: float = Field(0.0, description="Insurance cost")
    additional_costs: float = Field(0.0, description="Additional costs")
    trade_agreement: Optional[str] = Field(None, description="Applicable trade agreement")
    ad_cvd_applicable: bool = Field(False, description="Whether AD/CVD duties apply")
    special_programs: List[str] = Field(default_factory=list, description="Special programs")


class ScenarioComparisonRequest(BaseModel):
    """Scenario comparison request model."""
    scenario_ids: List[str] = Field(..., description="List of scenario IDs to compare", min_items=2)


@router.post("/create", response_model=dict)
async def create_scenario(request: ScenarioDataRequest):
    """
    Create a new scenario with detailed analysis.
    
    This endpoint collects all necessary details and provides:
    - Tariff rate calculation
    - Total cost analysis
    - Risk assessment
    - Recommendations
    - Opportunities
    """
    try:
        logger.info(f"📊 Creating scenario for product: {request.product_description}")
        
        # Generate scenario ID
        import time
        scenario_id = f"scenario_{int(time.time())}"
        
        # Create scenario
        result = await scenario_service.create_scenario(scenario_id, request.dict())
        
        if result.get("success"):
            return create_success_response(
                data=result,
                message="Scenario created and analyzed successfully"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to create scenario")
            )
            
    except Exception as e:
        logger.error(f"❌ Scenario creation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Scenario creation failed: {str(e)}"
        )


@router.post("/compare", response_model=dict)
async def compare_scenarios(request: ScenarioComparisonRequest):
    """
    Compare multiple scenarios to find the best option.
    
    This endpoint compares scenarios and provides:
    - Cost comparison
    - Best option identification
    - Potential savings
    - Detailed analysis
    """
    try:
        logger.info(f"📊 Comparing {len(request.scenario_ids)} scenarios")
        
        result = await scenario_service.compare_scenarios(request.scenario_ids)
        
        if result.get("success"):
            return create_success_response(
                data=result,
                message="Scenario comparison completed successfully"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to compare scenarios")
            )
            
    except Exception as e:
        logger.error(f"❌ Scenario comparison error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Scenario comparison failed: {str(e)}"
        )


@router.get("/list")
async def list_scenarios():
    """Get list of all created scenarios."""
    try:
        scenario_ids = scenario_service.list_scenarios()
        
        # Get basic info for each scenario
        scenarios = []
        for scenario_id in scenario_ids:
            scenario = scenario_service.get_scenario(scenario_id)
            if scenario:
                scenarios.append({
                    "scenario_id": scenario_id,
                    "product_description": scenario.product_description,
                    "hts_code": scenario.hts_code,
                    "base_value": scenario.base_value,
                    "origin_country": scenario.origin_country
                })
        
        return create_success_response(
            data={"scenarios": scenarios},
            message=f"Found {len(scenarios)} scenarios"
        )
        
    except Exception as e:
        logger.error(f"❌ List scenarios error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list scenarios: {str(e)}"
        )


@router.get("/{scenario_id}")
async def get_scenario(scenario_id: str):
    """Get detailed information about a specific scenario."""
    try:
        scenario = scenario_service.get_scenario(scenario_id)
        
        if scenario:
            # Re-analyze the scenario to get current data
            from app.services.scenario_service import ScenarioData
            analysis = await scenario_service._analyze_scenario(scenario)
            
            return create_success_response(
                data={
                    "scenario_id": scenario_id,
                    "data": scenario,
                    "analysis": analysis
                },
                message="Scenario retrieved successfully"
            )
        else:
            raise HTTPException(
                status_code=404,
                detail="Scenario not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Get scenario error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get scenario: {str(e)}"
        )


@router.delete("/{scenario_id}")
async def delete_scenario(scenario_id: str):
    """Delete a scenario."""
    try:
        success = scenario_service.delete_scenario(scenario_id)
        
        if success:
            return create_success_response(
                message="Scenario deleted successfully"
            )
        else:
            raise HTTPException(
                status_code=404,
                detail="Scenario not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Delete scenario error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete scenario: {str(e)}"
        )


@router.post("/analyze-quick")
async def quick_analysis(request: ScenarioDataRequest):
    """
    Quick scenario analysis without saving.
    
    This endpoint provides immediate analysis for a single scenario
    without creating a persistent scenario record.
    """
    try:
        logger.info(f"⚡ Quick analysis for: {request.product_description}")
        
        # Create temporary scenario
        from app.services.scenario_service import ScenarioData
        scenario = ScenarioData(
            product_description=request.product_description,
            hts_code=request.hts_code or "",
            base_value=request.base_value,
            quantity=request.quantity,
            origin_country=request.origin_country,
            destination_country=request.destination_country,
            currency=request.currency,
            shipping_cost=request.shipping_cost,
            insurance_cost=request.insurance_cost,
            additional_costs=request.additional_costs
        )
        
        # Analyze the scenario
        analysis = await scenario_service._analyze_scenario(scenario)
        
        return create_success_response(
            data={
                "scenario": scenario,
                "analysis": analysis
            },
            message="Quick analysis completed successfully"
        )
        
    except Exception as e:
        logger.error(f"❌ Quick analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Quick analysis failed: {str(e)}"
        ) 