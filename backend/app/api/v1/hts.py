from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
import pandas as pd
import os
from pydantic import BaseModel
from app.core.database import get_db
from app.models.hts import HTSRecord
from app.schemas.hts import HTSSearchRequest, HTSSearchResponse, HTSRecordResponse, HTSSuggestionResponse
from app.services.hts_service import HTSService
from loguru import logger

router = APIRouter()
hts_service = HTSService()

@router.on_event("startup")
async def startup_event():
    """Initialize HTS service on startup"""
    try:
        await hts_service.initialize()
        logger.info("HTS service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize HTS service: {e}")

@router.get("/search", response_model=HTSSearchResponse)
async def search_hts_codes(
    query: str = Query(..., description="Search query for HTS codes or descriptions"),
    limit: int = Query(10, description="Maximum number of results to return"),
):
    """Search for HTS codes by code or description (vector + substring search)"""
    if not query.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty")

    try:
        results = await hts_service.search_hts_codes(query, limit)
        
        return HTSSearchResponse(
            success=True,
            message=f"Found {len(results)} HTS codes",
            query=query,
            results=results,
            total_results=len(results)
        )
        
    except Exception as e:
        logger.error(f"HTS search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/code/{hts_code}", response_model=HTSRecordResponse)
async def get_hts_code(
    hts_code: str,
    db: Session = Depends(get_db)
):
    """Get specific HTS code details"""
    
    record = db.query(HTSRecord).filter(HTSRecord.hts_code == hts_code).first()
    
    if not record:
        # Try AI-powered lookup
        try:
            ai_record = await hts_service.get_hts_details(hts_code)
            if ai_record:
                return ai_record
        except Exception:
            pass
        
        raise HTTPException(status_code=404, detail="HTS code not found")
    
    return record

@router.get("/suggestions", response_model=HTSSuggestionResponse)
async def get_hts_suggestions(
    query: str = Query(..., description="Partial query for suggestions"),
    limit: int = Query(5, description="Maximum number of suggestions")
):
    """Get HTS code suggestions for autocomplete"""
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        suggestions = await hts_service.get_suggestions(query, limit)
        
        return HTSSuggestionResponse(
            success=True,
            message=f"Found {len(suggestions)} suggestions",
            query=query,
            suggestions=suggestions
        )
        
    except Exception as e:
        logger.error(f"HTS suggestions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/categories", response_model=List[str])
async def get_hts_categories(
    db: Session = Depends(get_db)
):
    """Get all available HTS categories"""
    
    categories = db.query(HTSRecord.category).distinct().filter(
        HTSRecord.category.isnot(None)
    ).all()
    
    return [cat[0] for cat in categories if cat[0]]

@router.get("/category/{category}", response_model=List[HTSRecordResponse])
async def get_hts_by_category(
    category: str,
    limit: int = Query(50, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Get HTS codes by category"""
    
    records = db.query(HTSRecord).filter(
        HTSRecord.category == category
    ).limit(limit).all()
    
    return records

@router.post("/import")
async def import_hts_data(
    db: Session = Depends(get_db)
):
    """Import HTS data from Excel file"""
    
    try:
        imported_count = await hts_service.import_from_excel(db)
        return {"message": f"Successfully imported {imported_count} HTS records"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")

@router.get("/statistics")
async def get_hts_statistics():
    """Get HTS code statistics"""
    try:
        stats = await hts_service.get_statistics()
        
        return {
            "success": True,
            "message": "Statistics retrieved successfully",
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"Get statistics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def hts_health():
    """Health check for HTS service"""
    try:
        stats = await hts_service.get_statistics()
        return {
            "status": "healthy",
            "service": "hts",
            "total_codes": stats.get("total_hts_codes", 0),
            "vector_documents": stats.get("vector_store_documents", 0)
        }
    except Exception as e:
        logger.error(f"HTS health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "hts",
            "error": str(e)
        } 