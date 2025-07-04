from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.services.ai_service import AIService
from app.services.hts_service import HTSService
from app.db.models import Scenario
from app.core.responses import ScenarioResponse, SuccessResponse
from loguru import logger
from datetime import datetime

router = APIRouter()

class ScenarioRequest(BaseModel):
    base_scenario: Dict[str, Any]  # hts_code, country, material_cost, tariff_rate
    changes: Dict[str, Any]  # what to change in the scenario
    scenario_name: Optional[str] = None

class ScenarioComparisonRequest(BaseModel):
    scenarios: List[Dict[str, Any]]  # multiple scenarios to compare

@router.post("/simulate", response_model=ScenarioResponse)
async def simulate_scenario(
    request: ScenarioRequest,
    db: AsyncSession = Depends(get_db)
):
    """Simulate a scenario change and calculate impact"""
    try:
        ai_service = AIService()
        hts_service = HTSService()
        
        # Use AI to simulate scenario
        simulation = await ai_service.simulate_scenario(request.base_scenario, request.changes)
        
        if simulation['success']:
            # Calculate base scenario costs
            base_hts_code = request.base_scenario.get('hts_code')
            base_country = request.base_scenario.get('country', 'US')
            base_material_cost = request.base_scenario.get('material_cost', 0)
            
            base_tariff_rate = await hts_service.get_tariff_rate(base_hts_code, base_country) or 0
            base_tariff_amount = base_material_cost * (base_tariff_rate / 100)
            base_total_cost = base_material_cost + base_tariff_amount
            
            # Store scenario in database
            scenario = Scenario(
                base_scenario=request.base_scenario,
                modified_scenario=simulation['simulation'],
                savings=float(simulation['simulation'].get('impact', {}).get('cost_change', '0').replace('$', '').replace(',', '')),
                percentage_change=float(simulation['simulation'].get('impact', {}).get('percentage_change', '0').replace('%', '')),
                risk_assessment=simulation['simulation'].get('risk_assessment', 'Unknown')
            )
            db.add(scenario)
            await db.commit()
            
            return ScenarioResponse(
                success=True,
                message="Scenario simulation completed successfully",
                base_scenario={
                    'hts_code': base_hts_code,
                    'country': base_country,
                    'material_cost': base_material_cost,
                    'tariff_rate': base_tariff_rate,
                    'tariff_amount': base_tariff_amount,
                    'total_cost': base_total_cost
                },
                modified_scenario=simulation['simulation'],
                savings=float(simulation['simulation'].get('impact', {}).get('cost_change', '0').replace('$', '').replace(',', '')),
                percentage_change=float(simulation['simulation'].get('impact', {}).get('percentage_change', '0').replace('%', ''))
            )
        else:
            return ScenarioResponse(
                success=False,
                message="Failed to simulate scenario",
                base_scenario=request.base_scenario,
                modified_scenario={},
                savings=0.0,
                percentage_change=0.0
            )
            
    except Exception as e:
        logger.error(f"Scenario simulation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compare", response_model=SuccessResponse)
async def compare_scenarios(request: ScenarioComparisonRequest):
    """Compare multiple scenarios"""
    try:
        ai_service = AIService()
        hts_service = HTSService()
        
        comparison_results = []
        
        for i, scenario in enumerate(request.scenarios):
            try:
                # Calculate base scenario
                base_hts_code = scenario.get('hts_code')
                base_country = scenario.get('country', 'US')
                base_material_cost = scenario.get('material_cost', 0)
                
                base_tariff_rate = await hts_service.get_tariff_rate(base_hts_code, base_country) or 0
                base_tariff_amount = base_material_cost * (base_tariff_rate / 100)
                base_total_cost = base_material_cost + base_tariff_amount
                
                comparison_results.append({
                    'scenario_id': i + 1,
                    'scenario_name': scenario.get('name', f'Scenario {i + 1}'),
                    'hts_code': base_hts_code,
                    'country': base_country,
                    'material_cost': base_material_cost,
                    'tariff_rate': base_tariff_rate,
                    'tariff_amount': base_tariff_amount,
                    'total_cost': base_total_cost
                })
                
            except Exception as e:
                comparison_results.append({
                    'scenario_id': i + 1,
                    'scenario_name': scenario.get('name', f'Scenario {i + 1}'),
                    'error': str(e)
                })
        
        # Sort by total cost
        comparison_results.sort(key=lambda x: x.get('total_cost', float('inf')))
        
        return SuccessResponse(
            success=True,
            message=f"Compared {len(comparison_results)} scenarios",
            data={
                'scenarios': comparison_results,
                'best_scenario': comparison_results[0] if comparison_results else None,
                'total_scenarios': len(comparison_results)
            }
        )
        
    except Exception as e:
        logger.error(f"Scenario comparison error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=SuccessResponse)
async def get_scenario_history(
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get recent scenario simulation history"""
    try:
        from sqlalchemy import select, desc
        
        result = await db.execute(
            select(Scenario)
            .order_by(desc(Scenario.created_at))
            .limit(limit)
        )
        
        scenarios = result.scalars().all()
        
        history = [
            {
                'id': scenario.id,
                'base_scenario': scenario.base_scenario,
                'modified_scenario': scenario.modified_scenario,
                'savings': scenario.savings,
                'percentage_change': scenario.percentage_change,
                'risk_assessment': scenario.risk_assessment,
                'created_at': scenario.created_at.isoformat()
            }
            for scenario in scenarios
        ]
        
        return SuccessResponse(
            success=True,
            message=f"Retrieved {len(history)} scenarios",
            data={
                'scenarios': history,
                'total_count': len(history)
            }
        )
        
    except Exception as e:
        logger.error(f"Get scenario history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates", response_model=SuccessResponse)
async def get_scenario_templates():
    """Get predefined scenario templates"""
    templates = [
        {
            'id': 'country_change',
            'name': 'Country of Origin Change',
            'description': 'Compare sourcing from different countries',
            'base_scenario': {
                'hts_code': '8471.30.01',
                'country': 'China',
                'material_cost': 500
            },
            'changes': {
                'country': 'Mexico'
            }
        },
        {
            'id': 'material_change',
            'name': 'Material Composition Change',
            'description': 'Compare different material compositions',
            'base_scenario': {
                'hts_code': '4015.19.05',
                'country': 'China',
                'material_cost': 100
            },
            'changes': {
                'material_composition': {'cotton': 80, 'polyester': 20}
            }
        },
        {
            'id': 'volume_change',
            'name': 'Volume Discount Scenario',
            'description': 'Analyze impact of volume changes',
            'base_scenario': {
                'hts_code': '8471.30.01',
                'country': 'China',
                'material_cost': 500
            },
            'changes': {
                'volume': 'large',
                'discount_rate': 0.15
            }
        }
    ]
    
    return SuccessResponse(
        success=True,
        message="Retrieved scenario templates",
        data={
            'templates': templates,
            'total_templates': len(templates)
        }
    )

@router.get("/health")
async def scenarios_health():
    """Check scenario simulation service health"""
    try:
        hts_service = HTSService()
        stats = await hts_service.get_statistics()
        
        return {
            "service": "scenario_simulation",
            "status": "healthy",
            "hts_statistics": stats
        }
        
    except Exception as e:
        logger.error(f"Scenarios health check error: {e}")
        return {
            "service": "scenario_simulation",
            "status": "unhealthy",
            "error": str(e)
        } 