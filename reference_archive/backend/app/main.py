from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
from loguru import logger
import os
from dotenv import load_dotenv

from app.core.config import settings
from app.api.v1 import router as api_router
from app.services.db_init import init_database

# Load environment variables
load_dotenv()

# Configure logging
logger.add("logs/app.log", rotation="10 MB", retention="7 days", level="INFO")

# Create FastAPI app
app = FastAPI(
    title="TariffAI - Intelligent HTS & Tariff Management",
    description="A comprehensive, AI-powered tariff management system",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting TariffAI application...")
    await init_database()
    logger.info("Application started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("Shutting down TariffAI application...")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with API information"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>TariffAI - Intelligent HTS & Tariff Management</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
            .container { max-width: 800px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 40px; }
            .endpoints { background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; }
            .endpoint { margin: 10px 0; padding: 10px; background: rgba(255,255,255,0.1); border-radius: 5px; }
            a { color: #ffd700; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚢 TariffAI</h1>
                <p>Intelligent HTS & Tariff Management System</p>
            </div>
            <div class="endpoints">
                <h2>API Endpoints</h2>
                <div class="endpoint">
                    <strong>📚 API Documentation:</strong> 
                    <a href="/api/docs" target="_blank">Swagger UI</a> | 
                    <a href="/api/redoc" target="_blank">ReDoc</a>
                </div>
                <div class="endpoint">
                    <strong>💬 Chat API:</strong> POST /api/v1/chat/
                </div>
                <div class="endpoint">
                    <strong>🔍 HTS Search:</strong> GET /api/v1/hts/search
                </div>
                <div class="endpoint">
                    <strong>🧮 Tariff Calculator:</strong> POST /api/v1/tariff/calculate
                </div>
                <div class="endpoint">
                    <strong>📊 Reports:</strong> GET /api/v1/reports/
                </div>
                <div class="endpoint">
                    <strong>📈 Scenarios:</strong> POST /api/v1/scenarios/
                </div>
                <div class="endpoint">
                    <strong>🔬 Material Analysis:</strong> POST /api/v1/materials/analyze
                </div>
                <div class="endpoint">
                    <strong>📥 Data Ingestion:</strong> POST /api/v1/data/ingest
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "TariffAI",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
