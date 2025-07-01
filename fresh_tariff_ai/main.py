"""
TariffAI - Fresh Consolidated Edition
Main FastAPI Application

This is the main entry point for the TariffAI application, combining
the best features from multiple approaches into a clean, modular architecture.
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn

from app.core.config import settings
from app.core.database import init_database
from app.api.v1.router import api_router
from app.services.ai_service import ai_service
from app.services.search_service import SearchService

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    """
    # Startup
    logger.info("🚀 Starting TariffAI...")
    
    try:
        # Initialize database and vector store
        await init_database()
        logger.info("✅ Database initialized")
        
        # Initialize AI services
        await ai_service.initialize()
        logger.info("✅ AI services initialized")
        
        # Initialize search service
        await SearchService.initialize()
        logger.info("✅ Search service initialized")
        
        logger.info("🌟 TariffAI startup complete!")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down TariffAI...")
    
    try:
        # Cleanup services
        await ai_service.cleanup()
        await SearchService.cleanup()
        
        logger.info("✅ TariffAI shutdown complete")
        
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
        description="Intelligent Tariff Management Platform",
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
    add_middleware(app)
    
    # Include API routes
    app.include_router(api_router, prefix="/api/v1")
    
    # Add health check endpoint
    @app.get("/health")
    async def health_check():
        """System health check endpoint"""
        return {
            "status": "healthy",
            "app": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
            "timestamp": time.time()
        }
    
    # Add root endpoint
    @app.get("/")
    async def root():
        """Root endpoint with API information"""
        return {
            "message": f"Welcome to {settings.app_name}",
            "version": settings.app_version,
            "docs": "/docs" if settings.is_development else "Documentation not available in production",
            "health": "/health"
        }
    
    # Mount static files for frontend
    try:
        app.mount("/static", StaticFiles(directory="frontend"), name="static")
    except RuntimeError:
        # Frontend directory doesn't exist, skip mounting
        pass
    
    return app


def add_middleware(app: FastAPI) -> None:
    """
    Add custom middleware to the application.
    
    Args:
        app: FastAPI application instance
    """
    
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        """Add processing time header to all responses"""
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
    
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log all incoming requests"""
        start_time = time.time()
        
        # Log request
        logger.info(
            f"📥 {request.method} {request.url.path} - "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )
        
        response = await call_next(request)
        
        # Log response
        duration = time.time() - start_time
        logger.info(
            f"📤 {request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Duration: {duration:.3f}s"
        )
        
        return response
    
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        """Add security headers to all responses"""
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        return response


# Create the application instance
app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development,
        log_level="info"
    ) 