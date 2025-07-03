"""
Data Ingestion API endpoints for TariffAI
Provides functionality to add knowledge to the system.
"""

import logging
import uuid
import pandas as pd
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.search_service import search_service
from app.core.responses import create_success_response, create_error_response

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


class DataIngestionRequest(BaseModel):
    """Data ingestion request model."""
    doc_type: str = Field(..., description="Document type")
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Document content", min_length=10)


@router.post("/ingest", response_model=dict)
async def ingest_data(request: DataIngestionRequest):
    """
    Ingest new data into the knowledge base.
    """
    try:
        logger.info(f"📚 Data ingestion request: {request.title}")
        
        # Generate unique document ID
        doc_id = str(uuid.uuid4())
        
        # Prepare metadata
        metadata = {
            "doc_type": request.doc_type,
            "title": request.title,
            "source": "user_upload",
            "ingestion_date": str(pd.Timestamp.now())
        }
        
        # Add to vector store
        success = await search_service.add_tariff_data(
            text=request.content,
            metadata=metadata,
            doc_id=doc_id
        )
        
        if success:
            return create_success_response(
                data={
                    "doc_id": doc_id,
                    "title": request.title,
                    "doc_type": request.doc_type
                },
                message="Data successfully ingested into knowledge base"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to ingest data into knowledge base"
            )
        
    except Exception as e:
        logger.error(f"❌ Data ingestion error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Data ingestion failed: {str(e)}"
        )


@router.get("/status")
async def get_ingestion_status():
    """Get data ingestion status and statistics."""
    try:
        # Get collection info
        collection = search_service.collection
        if collection:
            count = collection.count()
            return create_success_response(
                data={
                    "total_documents": count,
                    "status": "active"
                },
                message="Knowledge base status retrieved successfully"
            )
        else:
            return create_error_response(
                message="Knowledge base not available",
                error_code="KNOWLEDGE_BASE_UNAVAILABLE"
            )
        
    except Exception as e:
        logger.error(f"❌ Error getting ingestion status: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve ingestion status"
        ) 