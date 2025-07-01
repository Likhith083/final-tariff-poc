"""
Main FastAPI application for TariffAI
"""
import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.core.config import settings
from app.core.database import init_db, insert_sample_data
from app.api.v1.chat import router as chat_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting TariffAI application...")
    
    try:
        # Initialize database
        await init_db()
        await insert_sample_data()
        logger.info("✅ Database initialized successfully")
        
        logger.info("✅ TariffAI application started successfully")
        
    except Exception as e:
        logger.error(f"❌ Error during startup: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down TariffAI application...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Intelligent HTS & Tariff Management System",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    logger.error(f"Unhandled exception: {exc}")
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
    """Health check endpoint"""
    return {
        "success": True,
        "message": "TariffAI is healthy",
        "version": settings.app_version,
        "status": "operational"
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to TariffAI - Intelligent HTS & Tariff Management",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health"
    }


# Include API routers
app.include_router(chat_router, prefix="/api/v1")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    ) 