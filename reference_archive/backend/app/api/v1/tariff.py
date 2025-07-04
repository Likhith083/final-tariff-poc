from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.services.hts_service import HTSService
from app.db.models import TariffCalculation
from app.core.responses import TariffCalculationResponse, SuccessResponse
from loguru import logger
from datetime import datetime

router = APIRouter()

class TariffCalculationRequest(BaseModel):
    hts_code: str
    country_origin: str = "US"
    material_cost: float
    currency: str = "USD"
    freight_cost: Optional[float] = 0.0
    insurance_cost: Optional[float] = 0.0
    other_costs: Optional[float] = 0.0

class BulkTariffCalculationRequest(BaseModel):
    calculations: list[TariffCalculationRequest]

@router.post("/calculate", response_model=TariffCalculationResponse)
async def calculate_tariff(
    request: TariffCalculationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Calculate tariff and landed cost for a product"""
    try:
        hts_service = HTSService()
        
        # Get tariff rate
        tariff_rate = await hts_service.get_tariff_rate(request.hts_code, request.country_origin)
        
        if tariff_rate is None:
            raise HTTPException(
                status_code=404,
                detail=f"Tariff rate not found for HTS {request.hts_code} from {request.country_origin}"
            )
        
        # Calculate costs
        tariff_amount = request.material_cost * (tariff_rate / 100)
        total_landed_cost = (
            request.material_cost + 
            tariff_amount + 
            request.freight_cost + 
            request.insurance_cost + 
            request.other_costs
        )
        
        # Store calculation in database
        calculation = TariffCalculation(
            hts_code=request.hts_code,
            country_origin=request.country_origin,
            material_cost=request.material_cost,
            tariff_rate=tariff_rate,
            tariff_amount=tariff_amount,
            total_landed_cost=total_landed_cost,
            currency=request.currency
        )
        db.add(calculation)
        await db.commit()
        
        return TariffCalculationResponse(
            success=True,
            message="Tariff calculation completed successfully",
            hts_code=request.hts_code,
            country_origin=request.country_origin,
            material_cost=request.material_cost,
            tariff_rate=tariff_rate,
            tariff_amount=round(tariff_amount, 2),
            total_landed_cost=round(total_landed_cost, 2),
            currency=request.currency
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Tariff calculation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/calculate-bulk", response_model=SuccessResponse)
async def calculate_bulk_tariffs(
    request: BulkTariffCalculationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Calculate tariffs for multiple products"""
    try:
        hts_service = HTSService()
        results = []
        
        for calc_request in request.calculations:
            try:
                # Get tariff rate
                tariff_rate = await hts_service.get_tariff_rate(
                    calc_request.hts_code, 
                    calc_request.country_origin
                )
                
                if tariff_rate is None:
                    results.append({
                        'hts_code': calc_request.hts_code,
                        'success': False,
                        'error': f"Tariff rate not found for HTS {calc_request.hts_code}"
                    })
                    continue
                
                # Calculate costs
                tariff_amount = calc_request.material_cost * (tariff_rate / 100)
                total_landed_cost = (
                    calc_request.material_cost + 
                    tariff_amount + 
                    calc_request.freight_cost + 
                    calc_request.insurance_cost + 
                    calc_request.other_costs
                )
                
                # Store calculation
                calculation = TariffCalculation(
                    hts_code=calc_request.hts_code,
                    country_origin=calc_request.country_origin,
                    material_cost=calc_request.material_cost,
                    tariff_rate=tariff_rate,
                    tariff_amount=tariff_amount,
                    total_landed_cost=total_landed_cost,
                    currency=calc_request.currency
                )
                db.add(calculation)
                
                results.append({
                    'hts_code': calc_request.hts_code,
                    'success': True,
                    'tariff_rate': tariff_rate,
                    'tariff_amount': round(tariff_amount, 2),
                    'total_landed_cost': round(total_landed_cost, 2),
                    'currency': calc_request.currency
                })
                
            except Exception as e:
                results.append({
                    'hts_code': calc_request.hts_code,
                    'success': False,
                    'error': str(e)
                })
        
        await db.commit()
        
        return SuccessResponse(
            success=True,
            message=f"Processed {len(request.calculations)} calculations",
            data={
                'results': results,
                'total_processed': len(request.calculations),
                'successful': len([r for r in results if r['success']]),
                'failed': len([r for r in results if not r['success']])
            }
        )
        
    except Exception as e:
        logger.error(f"Bulk tariff calculation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=SuccessResponse)
async def get_calculation_history(
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get recent tariff calculation history"""
    try:
        from sqlalchemy import select, desc
        
        result = await db.execute(
            select(TariffCalculation)
            .order_by(desc(TariffCalculation.calculated_at))
            .limit(limit)
        )
        
        calculations = result.scalars().all()
        
        history = [
            {
                'id': calc.id,
                'hts_code': calc.hts_code,
                'country_origin': calc.country_origin,
                'material_cost': calc.material_cost,
                'tariff_rate': calc.tariff_rate,
                'tariff_amount': calc.tariff_amount,
                'total_landed_cost': calc.total_landed_cost,
                'currency': calc.currency,
                'calculated_at': calc.calculated_at.isoformat()
            }
            for calc in calculations
        ]
        
        return SuccessResponse(
            success=True,
            message=f"Retrieved {len(history)} calculations",
            data={
                'calculations': history,
                'total_count': len(history)
            }
        )
        
    except Exception as e:
        logger.error(f"Get calculation history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics", response_model=SuccessResponse)
async def get_calculation_statistics(db: AsyncSession = Depends(get_db)):
    """Get tariff calculation statistics"""
    try:
        from sqlalchemy import select, func
        
        # Get total calculations
        total_result = await db.execute(select(func.count(TariffCalculation.id)))
        total_calculations = total_result.scalar()
        
        # Get average tariff rate
        avg_rate_result = await db.execute(select(func.avg(TariffCalculation.tariff_rate)))
        avg_tariff_rate = avg_rate_result.scalar() or 0
        
        # Get total tariff amount
        total_tariff_result = await db.execute(select(func.sum(TariffCalculation.tariff_amount)))
        total_tariff_amount = total_tariff_result.scalar() or 0
        
        # Get most common HTS codes
        hts_count_result = await db.execute(
            select(TariffCalculation.hts_code, func.count(TariffCalculation.hts_code))
            .group_by(TariffCalculation.hts_code)
            .order_by(func.count(TariffCalculation.hts_code).desc())
            .limit(5)
        )
        top_hts_codes = [
            {'hts_code': hts_code, 'count': count}
            for hts_code, count in hts_count_result.all()
        ]
        
        return SuccessResponse(
            success=True,
            message="Statistics retrieved successfully",
            data={
                'total_calculations': total_calculations,
                'average_tariff_rate': round(avg_tariff_rate, 2),
                'total_tariff_amount': round(total_tariff_amount, 2),
                'top_hts_codes': top_hts_codes,
                'last_updated': datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Get calculation statistics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def tariff_health():
    """Check tariff calculator service health"""
    try:
        hts_service = HTSService()
        stats = await hts_service.get_statistics()
        
        return {
            "service": "tariff_calculator",
            "status": "healthy",
            "hts_statistics": stats
        }
        
    except Exception as e:
        logger.error(f"Tariff health check error: {e}")
        return {
            "service": "tariff_calculator",
            "status": "unhealthy",
            "error": str(e)
        }
