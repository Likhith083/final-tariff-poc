from fastapi import APIRouter
from app.api.v1 import chat, hts, tariff, materials, scenarios, reports, data_ingestion

# Create main router
router = APIRouter()

# Include all feature routers
router.include_router(chat.router, prefix="/chat", tags=["Chat"])
router.include_router(hts.router, prefix="/hts", tags=["HTS Search"])
router.include_router(tariff.router, prefix="/tariff", tags=["Tariff Calculator"])
router.include_router(materials.router, prefix="/materials", tags=["Material Analysis"])
router.include_router(scenarios.router, prefix="/scenarios", tags=["Scenario Simulation"])
router.include_router(reports.router, prefix="/reports", tags=["Reports"])
router.include_router(data_ingestion.router, prefix="/data", tags=["Data Ingestion"])
