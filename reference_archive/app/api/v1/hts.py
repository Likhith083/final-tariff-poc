from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.services.hts_service import HTSService
from app.services.ai_service import AIService
from app.core.responses import HTSSearchResponse, SuccessResponse
from loguru import logger
import time

router = APIRouter()

class HTSSearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 10
    country_origin: Optional[str] = "US"

class HTSClassificationRequest(BaseModel):
    product_description: str
    include_alternatives: Optional[bool] = True

@router.get("/search", response_model=HTSSearchResponse)
async def search_hts_codes(
    query: str = Query(..., description="Search query for HTS codes"),
    limit: int = Query(10, description="Maximum number of results"),
    country_origin: str = Query("US", description="Country of origin")
):
    """Search HTS codes by description or code"""
    start_time = time.time()
    
    try:
        hts_service = HTSService()
        results = await hts_service.search_hts_codes(query, limit)
        
        search_time = time.time() - start_time
        
        return HTSSearchResponse(
            success=True,
            message=f"Found {len(results)} HTS codes",
            query=query,
            results=results,
            total_results=len(results),
            search_time=round(search_time, 3)
        )
        
    except Exception as e:
        logger.error(f"HTS search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/classify", response_model=SuccessResponse)
async def classify_product(request: HTSClassificationRequest):
    """Classify a product and suggest HTS codes using AI"""
    try:
        ai_service = AIService()
        hts_service = HTSService()
        
        # Use AI to classify the product
        classification = await ai_service.classify_product(request.product_description)
        
        if classification['success']:
            # Get detailed information for the suggested HTS codes
            hts_details = []
            if 'classification' in classification:
                primary_code = classification['classification'].get('primary_hts_code')
                if primary_code:
                    hts_detail = await hts_service.get_hts_code(primary_code)
                    if hts_detail:
                        hts_details.append(hts_detail)
                
                # Get details for alternative codes
                if request.include_alternatives:
                    alternatives = classification['classification'].get('alternatives', [])
                    for alt_code in alternatives[:3]:  # Limit to 3 alternatives
                        alt_detail = await hts_service.get_hts_code(alt_code)
                        if alt_detail:
                            hts_details.append(alt_detail)
            
            return SuccessResponse(
                success=True,
                message="Product classified successfully",
                data={
                    'classification': classification['classification'],
                    'hts_details': hts_details,
                    'confidence': classification.get('confidence', 0.0)
                }
            )
        else:
            return SuccessResponse(
                success=False,
                message="Failed to classify product",
                data={
                    'response': classification.get('response', ''),
                    'error': classification.get('error', '')
                }
            )
            
    except Exception as e:
        logger.error(f"Product classification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/code/{hts_code}", response_model=SuccessResponse)
async def get_hts_code(hts_code: str):
    """Get detailed information for a specific HTS code"""
    try:
        hts_service = HTSService()
        hts_detail = await hts_service.get_hts_code(hts_code)
        
        if hts_detail:
            return SuccessResponse(
                success=True,
                message="HTS code found",
                data=hts_detail
            )
        else:
            raise HTTPException(status_code=404, detail="HTS code not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get HTS code error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tariff-rate/{hts_code}", response_model=SuccessResponse)
async def get_tariff_rate(
    hts_code: str,
    country_origin: str = Query("US", description="Country of origin")
):
    """Get tariff rate for a specific HTS code and country"""
    try:
        hts_service = HTSService()
        tariff_rate = await hts_service.get_tariff_rate(hts_code, country_origin)
        
        if tariff_rate is not None:
            return SuccessResponse(
                success=True,
                message="Tariff rate retrieved successfully",
                data={
                    'hts_code': hts_code,
                    'country_origin': country_origin,
                    'tariff_rate': tariff_rate
                }
            )
        else:
            raise HTTPException(
                status_code=404, 
                detail=f"Tariff rate not found for HTS {hts_code} from {country_origin}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get tariff rate error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics", response_model=SuccessResponse)
async def get_hts_statistics():
    """Get HTS code statistics"""
    try:
        hts_service = HTSService()
        stats = await hts_service.get_statistics()
        
        return SuccessResponse(
            success=True,
            message="Statistics retrieved successfully",
            data=stats
        )
        
    except Exception as e:
        logger.error(f"Get statistics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/suggestions", response_model=SuccessResponse)
async def get_hts_suggestions(
    query: str = Query(..., description="Partial query for suggestions"),
    limit: int = Query(5, description="Maximum number of suggestions")
):
    """Get HTS code suggestions for autocomplete"""
    try:
        hts_service = HTSService()
        suggestions = await hts_service.search_hts_codes(query, limit)
        
        # Format suggestions for autocomplete
        formatted_suggestions = []
        for suggestion in suggestions:
            formatted_suggestions.append({
                'hts_code': suggestion['hts_code'],
                'description': suggestion['description'],
                'display_text': f"{suggestion['hts_code']} - {suggestion['description']}"
            })
        
        return SuccessResponse(
            success=True,
            message=f"Found {len(formatted_suggestions)} suggestions",
            data={
                'suggestions': formatted_suggestions,
                'query': query
            }
        )
        
    except Exception as e:
        logger.error(f"Get suggestions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def hts_health():
    """Check HTS service health"""
    try:
        hts_service = HTSService()
        stats = await hts_service.get_statistics()
        
        return {
            "service": "hts_search",
            "status": "healthy",
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"HTS health check error: {e}")
        return {
            "service": "hts_search",
            "status": "unhealthy",
            "error": str(e)
        }
