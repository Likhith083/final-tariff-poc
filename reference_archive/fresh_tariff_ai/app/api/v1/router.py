"""
API Router for TariffAI v1
Consolidates all API endpoints into a clean, organized structure.
"""

from fastapi import APIRouter

from app.api.v1.chat import router as chat_router
from app.api.v1.hts import router as hts_router
from app.api.v1.tariff import router as tariff_router
from app.api.v1.risk import router as risk_router
from app.api.v1.scenario import router as scenario_router
from app.api.v1.data import router as data_router

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(chat_router, prefix="/chat", tags=["Chat"])
api_router.include_router(hts_router, prefix="/hts", tags=["HTS Search"])
api_router.include_router(tariff_router, prefix="/tariff", tags=["Tariff Calculations"])
api_router.include_router(risk_router, prefix="/risk", tags=["Risk Assessment"])
api_router.include_router(scenario_router, prefix="/scenario", tags=["Scenario Analysis"])
api_router.include_router(data_router, prefix="/data", tags=["Data Ingestion"])

# Add a simple status endpoint
@api_router.get("/status")
async def api_status():
    """Get API status information."""
    return {
        "status": "operational",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/api/v1/chat",
            "hts_search": "/api/v1/hts/search",
            "tariff_calculation": "/api/v1/tariff/calculate",
            "risk_assessment": "/api/v1/risk/assess",
            "scenario_analysis": "/api/v1/scenario/analyze",
            "data_ingestion": "/api/v1/data/ingest",
            "status": "/api/v1/status"
        }
    } 