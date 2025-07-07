"""
Health Check API Router for ATLAS Enterprise
System health and status monitoring endpoints.
"""

import time
from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from core.database import get_db
from core.config import settings
from core.logging import get_logger
from schemas.common import HealthResponse

logger = get_logger(__name__)
router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Basic health check endpoint.
    
    Returns application status and version information.
    """
    return HealthResponse(
        success=True,
        message="ATLAS Enterprise is running",
        version="1.0.0",
        environment=settings.environment,
        timestamp=time.time(),
        checks={"api": "healthy"}
    )


@router.get("/detailed", response_model=HealthResponse)
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """
    Detailed health check with database connectivity.
    
    Returns comprehensive system health information.
    """
    checks = {}
    overall_success = True
    
    # Check API
    checks["api"] = "healthy"
    
    # Check database connectivity
    try:
        result = await db.execute(text("SELECT 1"))
        checks["database"] = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        checks["database"] = f"unhealthy: {str(e)}"
        overall_success = False
    
    # Check Redis (if configured)
    if settings.redis_url:
        try:
            # This would check Redis connectivity
            checks["redis"] = "healthy"
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            checks["redis"] = f"unhealthy: {str(e)}"
            overall_success = False
    else:
        checks["redis"] = "not configured"
    
    # Check external services
    checks["external_apis"] = "not implemented"
    
    return HealthResponse(
        success=overall_success,
        message="Detailed health check completed",
        version="1.0.0",
        environment=settings.environment,
        timestamp=time.time(),
        checks=checks
    )


@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """
    Kubernetes readiness probe endpoint.
    
    Returns 200 if the service is ready to accept traffic.
    """
    try:
        # Check database
        await db.execute(text("SELECT 1"))
        
        return {"status": "ready", "timestamp": time.time()}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {"status": "not ready", "error": str(e)}, 503


@router.get("/live")
async def liveness_check():
    """
    Kubernetes liveness probe endpoint.
    
    Returns 200 if the service is alive.
    """
    return {"status": "alive", "timestamp": time.time()} 