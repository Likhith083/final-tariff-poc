"""
API v1 Router - Main router for all API endpoints
"""

from fastapi import APIRouter
from . import hts, scenario, analytics, chat, tariff, risk, data

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(hts.router, prefix="/hts", tags=["HTS Search"])
api_router.include_router(scenario.router, prefix="/scenario", tags=["Scenario Analysis"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(tariff.router, prefix="/tariff", tags=["Tariff"])
api_router.include_router(risk.router, prefix="/risk", tags=["Risk Assessment"])
api_router.include_router(data.router, prefix="/data", tags=["Data"])

# Health check endpoint
@api_router.get("/status")
async def get_status():
    """Get API status"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "tariff-ai-api"
    } 