from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.services.ai_service import AIService
from app.services.chroma_service import ChromaService
from app.db.models import MaterialAnalysis
from app.core.responses import MaterialAnalysisResponse, SuccessResponse
from loguru import logger
from datetime import datetime

router = APIRouter()

class MaterialAnalysisRequest(BaseModel):
    material_composition: Dict[str, float]  # material_name: percentage
    product_name: Optional[str] = None
    current_cost: Optional[float] = None
    target_savings: Optional[float] = None

class MaterialSearchRequest(BaseModel):
    query: str
    limit: int = 10

@router.post("/analyze", response_model=MaterialAnalysisResponse)
async def analyze_materials(
    request: MaterialAnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    """Analyze material composition and suggest alternatives"""
    try:
        ai_service = AIService()
        chroma_service = ChromaService()
        
        # Use AI to analyze materials
        analysis = await ai_service.analyze_materials(request.material_composition)
        
        if analysis['success']:
            # Store analysis in database
            material_analysis = MaterialAnalysis(
                original_composition=request.material_composition,
                suggested_composition=analysis['analysis'].get('alternatives', [{}])[0].get('composition', {}),
                cost_savings=float(analysis['analysis'].get('alternatives', [{}])[0].get('cost_savings', '0').replace('%', '')),
                quality_impact=analysis['analysis'].get('alternatives', [{}])[0].get('quality_impact', 'Unknown'),
                recommendations=analysis['analysis'].get('recommendations', [])
            )
            db.add(material_analysis)
            await db.commit()
            
            return MaterialAnalysisResponse(
                success=True,
                message="Material analysis completed successfully",
                original_composition=request.material_composition,
                suggested_composition=analysis['analysis'].get('alternatives', [{}])[0].get('composition', {}),
                cost_savings=float(analysis['analysis'].get('alternatives', [{}])[0].get('cost_savings', '0').replace('%', '')),
                quality_impact=analysis['analysis'].get('alternatives', [{}])[0].get('quality_impact', 'Unknown'),
                recommendations=analysis['analysis'].get('recommendations', [])
            )
        else:
            return MaterialAnalysisResponse(
                success=False,
                message="Failed to analyze materials",
                original_composition=request.material_composition,
                suggested_composition={},
                cost_savings=0.0,
                quality_impact="Unknown",
                recommendations=[analysis.get('response', 'Analysis failed')]
            )
            
    except Exception as e:
        logger.error(f"Material analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=SuccessResponse)
async def search_materials(request: MaterialSearchRequest):
    """Search for materials and compositions"""
    try:
        chroma_service = ChromaService()
        results = await chroma_service.search_materials(request.query, request.limit)
        
        return SuccessResponse(
            success=True,
            message=f"Found {len(results)} materials",
            data={
                'query': request.query,
                'results': results,
                'total_results': len(results)
            }
        )
        
    except Exception as e:
        logger.error(f"Material search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=SuccessResponse)
async def get_analysis_history(
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get recent material analysis history"""
    try:
        from sqlalchemy import select, desc
        
        result = await db.execute(
            select(MaterialAnalysis)
            .order_by(desc(MaterialAnalysis.analyzed_at))
            .limit(limit)
        )
        
        analyses = result.scalars().all()
        
        history = [
            {
                'id': analysis.id,
                'original_composition': analysis.original_composition,
                'suggested_composition': analysis.suggested_composition,
                'cost_savings': analysis.cost_savings,
                'quality_impact': analysis.quality_impact,
                'recommendations': analysis.recommendations,
                'analyzed_at': analysis.analyzed_at.isoformat()
            }
            for analysis in analyses
        ]
        
        return SuccessResponse(
            success=True,
            message=f"Retrieved {len(history)} analyses",
            data={
                'analyses': history,
                'total_count': len(history)
            }
        )
        
    except Exception as e:
        logger.error(f"Get analysis history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def materials_health():
    """Check material analysis service health"""
    try:
        chroma_service = ChromaService()
        stats = await chroma_service.get_collection_stats("materials")
        
        return {
            "service": "material_analysis",
            "status": "healthy",
            "chroma_stats": stats
        }
        
    except Exception as e:
        logger.error(f"Materials health check error: {e}")
        return {
            "service": "material_analysis",
            "status": "unhealthy",
            "error": str(e)
        } 