"""
ATLAS Enterprise FastAPI Application
Main entry point for the tariff management API.
"""

import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import settings
from core.database import init_db, close_db, check_db_health
from core.logging import setup_logging, LoggingMiddleware, get_logger

# Setup logging first
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    
    # Startup
    logger.info("🚀 Starting ATLAS Enterprise API", version=settings.app_version)
    
    try:
        # Initialize database
        await init_db()
        logger.info("✅ Database initialized successfully")
        
        # Check database health
        db_healthy = await check_db_health()
        if not db_healthy:
            logger.error("❌ Database health check failed")
            raise Exception("Database not accessible")
        
        logger.info("🌟 ATLAS Enterprise startup complete!")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down ATLAS Enterprise API")
    
    try:
        await close_db()
        logger.info("✅ ATLAS Enterprise shutdown complete")
        
    except Exception as e:
        logger.error(f"❌ Shutdown error: {e}")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured application instance
    """
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Enterprise-grade tariff management and trade intelligence platform",
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        openapi_url="/openapi.json" if settings.is_development else None,
        lifespan=lifespan,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add custom middleware
    app.add_middleware(LoggingMiddleware)
    
    # Add request timing middleware
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Internal server error",
                "error_code": "INTERNAL_ERROR"
            }
        )
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Comprehensive health check endpoint."""
        
        # Check database
        db_healthy = await check_db_health()
        
        health_status = {
            "success": True,
            "message": "ATLAS Enterprise is healthy",
            "version": settings.app_version,
            "environment": settings.environment,
            "timestamp": time.time(),
            "checks": {
                "database": "healthy" if db_healthy else "unhealthy",
                "api": "healthy"
            }
        }
        
        # Set overall status
        if not db_healthy:
            health_status["success"] = False
            health_status["message"] = "ATLAS Enterprise has health issues"
        
        status_code = 200 if health_status["success"] else 503
        return JSONResponse(content=health_status, status_code=status_code)
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint with API information."""
        return {
            "message": f"Welcome to {settings.app_name}",
            "version": settings.app_version,
            "environment": settings.environment,
            "docs": "/docs" if settings.is_development else "Documentation not available in production",
            "health": "/health",
            "api_prefix": "/api/v1"
        }
    
    # Include API routers
    from api.v1.router import api_router
    app.include_router(api_router)
    
    return app


# Create the application instance
app = create_app()


# Development server entry point
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=settings.is_development,
    ) 