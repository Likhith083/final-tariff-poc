from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from dotenv import load_dotenv

from app.api.v1 import chat, hts, calculator
from app.core.config import settings
from app.core.database import engine, Base

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Tariff AI Backend",
    description="AI-powered tariff management and analysis system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes (authentication removed for now)
app.include_router(chat.router, prefix="/api/v1/chat", tags=["AI Chat"])
app.include_router(hts.router, prefix="/api/v1/hts", tags=["HTS Lookup"])
app.include_router(calculator.router, prefix="/api/v1/calculator", tags=["Tariff Calculator"])

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Tariff AI Backend is running"}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Tariff AI Backend",
        "docs": "/docs",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 