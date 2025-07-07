"""
Main API Router for ATLAS Enterprise v1
Combines all API endpoint routers.
"""

from fastapi import APIRouter

from api.v1.auth import router as auth_router
from api.v1.tariff import router as tariff_router
from api.v1.health import router as health_router
from api.v1.data import router as data_router
from api.v1.ai import router as ai_router

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Include all endpoint routers
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(tariff_router)
api_router.include_router(data_router)
api_router.include_router(ai_router) 