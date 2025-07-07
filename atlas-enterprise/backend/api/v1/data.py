"""
Data API endpoints for ATLAS Enterprise
Endpoints for tariff data and knowledge base access.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.responses import success_response, error_response
from services.data_ingestion_service import data_ingestion_service
from services.vector_service import vector_service
from core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/data", tags=["data"])


@router.get("/health")
async def data_health_check():
    """Check data services health."""
    try:
        health_status = await data_ingestion_service.health_check()
        return success_response(
            data=health_status,
            message="Data services health check completed"
        )
    except Exception as e:
        logger.error(f"Data health check failed: {e}")
        return error_response(
            message="Data health check failed",
            error_code="DATA_HEALTH_ERROR"
        )


@router.get("/tariff")
async def load_tariff_data():
    """Load tariff data from Excel file."""
    try:
        result = await data_ingestion_service.load_tariff_data()
        
        if result.get("success"):
            return success_response(
                data=result,
                message="Tariff data loaded successfully"
            )
        else:
            return error_response(
                message=result.get("error", "Failed to load tariff data"),
                error_code="TARIFF_LOAD_ERROR"
            )
            
    except Exception as e:
        logger.error(f"Error loading tariff data: {e}")
        return error_response(
            message="Failed to load tariff data",
            error_code="TARIFF_LOAD_ERROR"
        )


@router.get("/tariff/{hts_code}")
async def get_tariff_by_hts(hts_code: str):
    """Get tariff information by HTS code."""
    try:
        result = await data_ingestion_service.get_tariff_by_hts(hts_code)
        
        if result.get("success"):
            return success_response(
                data=result,
                message=f"Tariff data for HTS {hts_code} retrieved successfully"
            )
        else:
            return error_response(
                message=result.get("error", "Failed to get tariff data"),
                error_code="TARIFF_LOOKUP_ERROR"
            )
            
    except Exception as e:
        logger.error(f"Error getting tariff for HTS {hts_code}: {e}")
        return error_response(
            message="Failed to retrieve tariff data",
            error_code="TARIFF_LOOKUP_ERROR"
        )


@router.get("/knowledge")
async def load_knowledge_base():
    """Load knowledge base from JSON files."""
    try:
        result = await data_ingestion_service.load_knowledge_base()
        
        if result.get("success"):
            return success_response(
                data=result,
                message="Knowledge base loaded successfully"
            )
        else:
            return error_response(
                message=result.get("error", "Failed to load knowledge base"),
                error_code="KNOWLEDGE_LOAD_ERROR"
            )
            
    except Exception as e:
        logger.error(f"Error loading knowledge base: {e}")
        return error_response(
            message="Failed to load knowledge base",
            error_code="KNOWLEDGE_LOAD_ERROR"
        )


@router.post("/knowledge/ingest")
async def ingest_knowledge_base(db: AsyncSession = Depends(get_db)):
    """Ingest knowledge base into vector store."""
    try:
        # Load knowledge base
        knowledge_result = await data_ingestion_service.load_knowledge_base()
        
        if not knowledge_result.get("success"):
            return error_response(
                message="Failed to load knowledge base",
                error_code="KNOWLEDGE_LOAD_ERROR"
            )
        
        # Ingest into vector store
        ingest_result = await data_ingestion_service.ingest_knowledge_to_vector_store(
            db, knowledge_result["data"]
        )
        
        if ingest_result.get("success"):
            return success_response(
                data=ingest_result,
                message="Knowledge base ingested successfully"
            )
        else:
            return error_response(
                message=ingest_result.get("error", "Failed to ingest knowledge base"),
                error_code="KNOWLEDGE_INGEST_ERROR"
            )
            
    except Exception as e:
        logger.error(f"Error ingesting knowledge base: {e}")
        return error_response(
            message="Failed to ingest knowledge base",
            error_code="KNOWLEDGE_INGEST_ERROR"
        )


@router.get("/knowledge/search")
async def search_knowledge_base(
    query: str = Query(..., description="Search query"),
    top_k: int = Query(5, description="Number of results to return")
):
    """Search knowledge base using vector similarity."""
    try:
        results = await data_ingestion_service.search_knowledge_base(query, top_k)
        
        return success_response(
            data={
                "query": query,
                "results": results,
                "count": len(results)
            },
            message="Knowledge base search completed"
        )
        
    except Exception as e:
        logger.error(f"Error searching knowledge base: {e}")
        return error_response(
            message="Failed to search knowledge base",
            error_code="KNOWLEDGE_SEARCH_ERROR"
        )


@router.get("/vector/stats")
async def get_vector_stats():
    """Get vector store statistics."""
    try:
        await vector_service.initialize()
        stats = await vector_service.get_collection_stats()
        
        return success_response(
            data=stats,
            message="Vector store statistics retrieved"
        )
        
    except Exception as e:
        logger.error(f"Error getting vector stats: {e}")
        return error_response(
            message="Failed to get vector statistics",
            error_code="VECTOR_STATS_ERROR"
        )


@router.get("/summary")
async def get_data_summary():
    """Get summary of all available data."""
    try:
        # Get health status
        health = await data_ingestion_service.health_check()
        
        # Get vector stats
        vector_stats = {}
        try:
            await vector_service.initialize()
            vector_stats = await vector_service.get_collection_stats()
        except Exception:
            vector_stats = {"error": "Vector service unavailable"}
        
        # Get tariff data summary
        tariff_summary = {}
        try:
            tariff_data = await data_ingestion_service.load_tariff_data()
            if tariff_data.get("success"):
                tariff_summary = tariff_data.get("summary", {})
        except Exception:
            tariff_summary = {"error": "Tariff data unavailable"}
        
        # Get knowledge base summary
        knowledge_summary = {}
        try:
            knowledge_data = await data_ingestion_service.load_knowledge_base()
            if knowledge_data.get("success"):
                knowledge_summary = knowledge_data.get("summary", {})
        except Exception:
            knowledge_summary = {"error": "Knowledge base unavailable"}
        
        summary = {
            "health": health,
            "vector_store": vector_stats,
            "tariff_data": tariff_summary,
            "knowledge_base": knowledge_summary,
            "timestamp": "2024-01-01T00:00:00Z"  # You might want to use actual timestamp
        }
        
        return success_response(
            data=summary,
            message="Data summary retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting data summary: {e}")
        return error_response(
            message="Failed to get data summary",
            error_code="DATA_SUMMARY_ERROR"
        ) 