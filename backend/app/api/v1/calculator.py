from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.core.database import get_db
from app.models.tariff import TariffCalculation
from app.schemas.tariff import (
    CalculationRequest, CalculationResponse, 
    TariffCalculationResponse
)
from app.services.calculator_service import CalculatorService

router = APIRouter()
calculator_service = CalculatorService()

@router.post("/calculate", response_model=CalculationResponse)
async def calculate_tariff(
    request: CalculationRequest,
    db: Session = Depends(get_db)
):
    """Calculate tariff duty for a given HTS code and values"""
    
    try:
        # Perform calculation
        result = await calculator_service.calculate_duty(
            hts_code=request.hts_code,
            quantity=request.quantity,
            unit_price=request.unit_price,
            description=request.description
        )
        
        # Save calculation to database (simplified without user authentication)
        calculation = TariffCalculation(
            user_id=1,  # Default user ID
            hts_code=request.hts_code,
            description=result.get("description", request.description),
            quantity=request.quantity,
            unit_price=request.unit_price,
            total_value=result["total_value"],
            duty_rate=result["duty_rate"],
            duty_amount=result["duty_amount"],
            total_with_duty=result["total_with_duty"],
            calculation_details=result
        )
        db.add(calculation)
        db.commit()
        db.refresh(calculation)
        
        return CalculationResponse(
            hts_code=request.hts_code,
            description=result.get("description", request.description or ""),
            quantity=request.quantity,
            unit_price=request.unit_price,
            total_value=result["total_value"],
            duty_rate=result["duty_rate"],
            duty_amount=result["duty_amount"],
            total_with_duty=result["total_with_duty"],
            calculation_id=calculation.id
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")

@router.get("/history", response_model=List[TariffCalculationResponse])
async def get_calculation_history(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get calculation history (simplified without user authentication)"""
    
    calculations = db.query(TariffCalculation).order_by(TariffCalculation.created_at.desc()).limit(limit).all()
    
    return calculations

@router.get("/history/{calculation_id}", response_model=TariffCalculationResponse)
async def get_calculation_details(
    calculation_id: int,
    db: Session = Depends(get_db)
):
    """Get details of a specific calculation (simplified without user authentication)"""
    
    calculation = db.query(TariffCalculation).filter(
        TariffCalculation.id == calculation_id
    ).first()
    
    if not calculation:
        raise HTTPException(status_code=404, detail="Calculation not found")
    
    return calculation

@router.delete("/history/{calculation_id}")
async def delete_calculation(
    calculation_id: int,
    db: Session = Depends(get_db)
):
    """Delete a calculation from history (simplified without user authentication)"""
    
    calculation = db.query(TariffCalculation).filter(
        TariffCalculation.id == calculation_id
    ).first()
    
    if not calculation:
        raise HTTPException(status_code=404, detail="Calculation not found")
    
    db.delete(calculation)
    db.commit()
    
    return {"message": "Calculation deleted successfully"}

@router.post("/batch")
async def batch_calculate(
    requests: List[CalculationRequest],
    db: Session = Depends(get_db)
):
    """Calculate tariffs for multiple items at once"""
    
    if len(requests) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 items per batch")
    
    results = []
    
    for request in requests:
        try:
            result = await calculator_service.calculate_duty(
                hts_code=request.hts_code,
                quantity=request.quantity,
                unit_price=request.unit_price,
                description=request.description
            )
            
            # Save to database (simplified without user authentication)
            calculation = TariffCalculation(
                user_id=1,  # Default user ID
                hts_code=request.hts_code,
                description=result.get("description", request.description),
                quantity=request.quantity,
                unit_price=request.unit_price,
                total_value=result["total_value"],
                duty_rate=result["duty_rate"],
                duty_amount=result["duty_amount"],
                total_with_duty=result["total_with_duty"],
                calculation_details=result
            )
            db.add(calculation)
            
            results.append({
                "hts_code": request.hts_code,
                "description": result.get("description", request.description or ""),
                "quantity": request.quantity,
                "unit_price": request.unit_price,
                "total_value": result["total_value"],
                "duty_rate": result["duty_rate"],
                "duty_amount": result["duty_amount"],
                "total_with_duty": result["total_with_duty"],
                "calculation_id": calculation.id
            })
            
        except Exception as e:
            results.append({
                "hts_code": request.hts_code,
                "error": str(e)
            })
    
    db.commit()
    
    return {
        "results": results,
        "total_items": len(requests),
        "successful_calculations": len([r for r in results if "error" not in r])
    }

@router.get("/summary")
async def get_calculation_summary(
    db: Session = Depends(get_db)
):
    """Get summary statistics of calculations (simplified without user authentication)"""
    
    total_calculations = db.query(TariffCalculation).count()
    
    total_duty_paid = db.query(TariffCalculation).with_entities(func.sum(TariffCalculation.duty_amount)).scalar() or 0
    
    total_value = db.query(TariffCalculation).with_entities(func.sum(TariffCalculation.total_value)).scalar() or 0
    
    return {
        "total_calculations": total_calculations,
        "total_duty_paid": float(total_duty_paid),
        "total_value": float(total_value),
        "average_duty_rate": float(total_duty_paid / total_value * 100) if total_value > 0 else 0
    } 