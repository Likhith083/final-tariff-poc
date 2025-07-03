from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional

from app.core.database import get_db
from app.models.hts import HTSRecord
from app.schemas.hts import HTSSearchRequest, HTSSearchResponse, HTSRecordResponse
from app.services.hts_service import HTSService

router = APIRouter()
hts_service = HTSService()

@router.get("/search", response_model=HTSSearchResponse)
async def search_hts_codes(
    query: str = Query(..., description="Search query for HTS codes or descriptions"),
    limit: int = Query(10, description="Maximum number of results to return"),
    db: Session = Depends(get_db)
):
    """Search for HTS codes by code or description (case-insensitive, ignore periods)"""
    
    if not query.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty")

    # Normalize query for code search (remove periods)
    normalized_query = query.replace('.', '').lower()

    # Search in database (case-insensitive, ignore periods in code)
    results = db.query(HTSRecord).filter(
        or_(
            HTSRecord.hts_code.ilike(f"%{query}%"),
            HTSRecord.hts_code.ilike(f"%{normalized_query}%"),
            HTSRecord.description.ilike(f"%{query}%"),
            HTSRecord.category.ilike(f"%{query}%")
        )
    ).limit(limit).all()
    
    # If no results in database, try AI-powered search
    if not results:
        try:
            ai_results = await hts_service.ai_search(query, limit)
            return HTSSearchResponse(
                results=ai_results,
                total_count=len(ai_results),
                query=query
            )
        except Exception as e:
            # Return empty results if AI search fails
            return HTSSearchResponse(
                results=[],
                total_count=0,
                query=query
            )
    
    return HTSSearchResponse(
        results=results,
        total_count=len(results),
        query=query
    )

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

@router.get("/suggestions", response_model=List[str])
async def get_hts_suggestions(
    query: str = Query(..., description="Partial HTS code or description for suggestions"),
    limit: int = Query(5, description="Maximum number of suggestions"),
    db: Session = Depends(get_db)
):
    """Get HTS code suggestions for autocomplete"""
    
    if len(query.strip()) < 2:
        raise HTTPException(status_code=400, detail="Query must be at least 2 characters")
    
    # Get suggestions from database
    suggestions = db.query(HTSRecord.hts_code).filter(
        HTSRecord.hts_code.startswith(query)
    ).limit(limit).all()
    
    # If not enough suggestions, add description-based ones
    if len(suggestions) < limit:
        desc_suggestions = db.query(HTSRecord.hts_code).filter(
            HTSRecord.description.contains(query)
        ).limit(limit - len(suggestions)).all()
        suggestions.extend(desc_suggestions)
    
    return [s[0] for s in suggestions]

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

@router.get("/stats")
async def get_hts_stats(
    db: Session = Depends(get_db)
):
    """Get HTS database statistics"""
    
    total_records = db.query(HTSRecord).count()
    total_categories = db.query(HTSRecord.category).distinct().count()
    
    return {
        "total_records": total_records,
        "total_categories": total_categories,
        "last_updated": "2025-01-01"  # This would be dynamic in production
    } 