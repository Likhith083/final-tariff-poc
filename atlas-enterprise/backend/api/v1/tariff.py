"""
Tariff API Router for ATLAS Enterprise
HTS code search, tariff calculations, and sourcing comparisons.
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.logging import get_logger
from services.tariff_database_service import TariffDatabaseService
from services.tariff_calculation_engine import TariffCalculationEngine
from schemas.tariff import (
    HTSSearchRequest,
    HTSSearchResponse,
    HTSCodeResponse,
    TariffCalculationRequest,
    TariffCalculationResponse,
    SourcingComparisonRequest,
    SourcingComparisonResponse,
    ChapterSummaryResponse,
    ChapterSummary
)
from schemas.common import SuccessResponse, ErrorResponse
from api.dependencies import get_current_user
from models.user import User

logger = get_logger(__name__)
router = APIRouter(prefix="/tariff", tags=["tariff"])


@router.get("/hts/search", response_model=HTSSearchResponse)
async def search_hts_codes(
    query: str = Query(..., description="Search query (code or description)"),
    chapter: Optional[str] = Query(None, description="Filter by chapter (2 digits)"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search HTS codes by description or code.
    
    - **query**: Search term to find HTS codes
    - **chapter**: Optional chapter filter (e.g., "01", "84")
    - **limit**: Maximum number of results (1-100)
    """
    try:
        start_time = datetime.utcnow()
        
        # Perform search
        hts_codes = await TariffDatabaseService.search_hts_codes(
            db, query, limit, chapter
        )
        
        # Convert to response format
        response_data = [
            HTSCodeResponse.model_validate(hts_code) for hts_code in hts_codes
        ]
        
        # Calculate search time
        search_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        return HTSSearchResponse(
            success=True,
            message=f"Found {len(response_data)} HTS codes",
            data=response_data,
            total_results=len(response_data),
            search_query=query,
            search_time_ms=search_time
        )
        
    except Exception as e:
        logger.error(f"Error searching HTS codes: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error searching HTS codes: {str(e)}"
        )


@router.get("/hts/{hts_code}", response_model=SuccessResponse[HTSCodeResponse])
async def get_hts_code(
    hts_code: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get specific HTS code by code.
    
    - **hts_code**: 10-digit HTS code (with or without dots)
    """
    try:
        hts_obj = await TariffDatabaseService.get_hts_code_by_code(db, hts_code)
        
        if not hts_obj:
            raise HTTPException(
                status_code=404,
                detail=f"HTS code not found: {hts_code}"
            )
        
        response_data = HTSCodeResponse.model_validate(hts_obj)
        
        return SuccessResponse(
            success=True,
            message=f"HTS code found: {hts_code}",
            data=response_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting HTS code {hts_code}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting HTS code: {str(e)}"
        )


@router.get("/chapters", response_model=ChapterSummaryResponse)
async def get_chapters_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get summary of all HTS chapters with code counts.
    """
    try:
        chapters_data = await TariffDatabaseService.get_chapters_summary(db)
        
        response_data = [
            ChapterSummary(**chapter) for chapter in chapters_data
        ]
        
        return ChapterSummaryResponse(
            success=True,
            message=f"Retrieved {len(response_data)} HTS chapters",
            data=response_data
        )
        
    except Exception as e:
        logger.error(f"Error getting chapters summary: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting chapters summary: {str(e)}"
        )


@router.post("/calculate", response_model=TariffCalculationResponse)
async def calculate_tariff(
    request: TariffCalculationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Calculate comprehensive landed cost for a product.
    
    Calculates:
    - Duty amount based on tariff rates
    - Antidumping and countervailing duties
    - Merchandise Processing Fee (MPF)
    - Harbor Maintenance Fee (HMF)
    - Total landed cost
    """
    try:
        # Perform calculation
        result = await TariffCalculationEngine.calculate_landed_cost(
            db=db,
            hts_code=request.hts_code,
            country_code=request.country_code,
            product_value=request.product_value,
            quantity=request.quantity,
            freight_cost=request.freight_cost,
            insurance_cost=request.insurance_cost,
            other_costs=request.other_costs,
            currency=request.currency,
            user_id=current_user.id
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Calculation failed")
            )
        
        return TariffCalculationResponse(
            success=True,
            message="Calculation completed successfully",
            data=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating tariff: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating tariff: {str(e)}"
        )


@router.post("/compare-sourcing", response_model=SourcingComparisonResponse)
async def compare_sourcing_options(
    request: SourcingComparisonRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Compare sourcing options across multiple countries.
    
    Returns ranked list of countries by total landed cost with:
    - Cost breakdown for each country
    - Applicable trade preferences
    - Risk assessment
    - Savings analysis
    """
    try:
        # Perform comparison
        result = await TariffCalculationEngine.compare_sourcing_options(
            db=db,
            hts_code=request.hts_code,
            product_value=request.product_value,
            countries=request.countries,
            quantity=request.quantity,
            freight_cost=request.freight_cost,
            insurance_cost=request.insurance_cost,
            other_costs=request.other_costs,
            currency=request.currency,
            user_id=current_user.id
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Comparison failed")
            )
        
        return SourcingComparisonResponse(
            success=True,
            message=f"Compared {result['total_countries_compared']} countries",
            data=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing sourcing options: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error comparing sourcing options: {str(e)}"
        )


@router.get("/popular-codes", response_model=SuccessResponse[List[HTSCodeResponse]])
async def get_popular_hts_codes(
    limit: int = Query(10, ge=1, le=50, description="Number of codes to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get most popular/frequently used HTS codes.
    
    - **limit**: Maximum number of codes to return (1-50)
    """
    try:
        hts_codes = await TariffDatabaseService.get_popular_hts_codes(db, limit)
        
        response_data = [
            HTSCodeResponse.model_validate(hts_code) for hts_code in hts_codes
        ]
        
        return SuccessResponse(
            success=True,
            message=f"Retrieved {len(response_data)} popular HTS codes",
            data=response_data
        )
        
    except Exception as e:
        logger.error(f"Error getting popular HTS codes: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting popular HTS codes: {str(e)}"
        )


@router.get("/validate/{hts_code}")
async def validate_hts_code(
    hts_code: str,
    current_user: User = Depends(get_current_user)
):
    """
    Validate HTS code format and structure.
    
    - **hts_code**: HTS code to validate
    """
    try:
        validation_result = await TariffDatabaseService.validate_hts_code(hts_code)
        
        return {
            "success": True,
            "message": "HTS code validation completed",
            "data": validation_result
        }
        
    except Exception as e:
        logger.error(f"Error validating HTS code {hts_code}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error validating HTS code: {str(e)}"
        ) 