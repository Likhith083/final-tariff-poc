#!/usr/bin/env python3
"""
TariffAI Backend - Main Entry Point
===================================

Enterprise-grade tariff management chatbot with AI-powered insights.
Provides RESTful APIs for tariff calculations, HTS lookups, scenario analysis,
and more.

Author: TariffAI Team
Version: 1.0.0
"""

import uvicorn
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import logging
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.core.config import settings
from app.core.database import init_database
from app.api.v1.router import api_router

# Configure logging with proper encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="TariffAI Backend",
    description="Enterprise-grade tariff management chatbot with AI-powered insights",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    logger.info("🚀 Initializing TariffAI Backend...")
    try:
        await init_database()
        logger.info("✅ Backend initialization complete")
    except Exception as e:
        logger.error(f"❌ Backend initialization failed: {e}")
        raise

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "TariffAI Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "tariff-ai-backend"}

if __name__ == "__main__":
    print("🚀 Starting TariffAI Backend...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
