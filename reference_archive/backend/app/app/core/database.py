"""
Database initialization and management for TariffAI Backend
"""

import logging
import asyncio
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from .config import settings
from ..db.base import Base
from ..db.models import User, Product, Tariff, Alert, Scenario, Report

logger = logging.getLogger(__name__)

# Global variables
engine = None
SessionLocal = None
chroma_client = None
embedding_model = None
tariff_data = None

def get_database_url():
    """Get database URL from settings"""
    if settings.database_url:
        return settings.database_url
    else:
        # Default to SQLite for development
        return "sqlite:///./tariff_ai.db"

def create_database_engine():
    """Create SQLAlchemy engine"""
    global engine, SessionLocal
    
    database_url = get_database_url()
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False} if "sqlite" in database_url else {}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    logger.info(f"✅ Database engine created: {database_url}")

def get_db():
    """Get database session"""
    if SessionLocal is None:
        create_database_engine()
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_database():
    """Initialize database and create tables"""
    global engine
    
    try:
        # Create database engine
        create_database_engine()
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created")
        
        # Initialize ChromaDB
        await init_chromadb()
        
        # Load tariff data
        await load_tariff_data()
        
        logger.info("✅ Database initialization complete")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

async def init_chromadb():
    """Initialize ChromaDB for semantic search"""
    global chroma_client, embedding_model
    
    try:
        # Initialize ChromaDB client
        chroma_client = chromadb.PersistentClient(
            path="./data/chroma",
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Load embedding model
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        logger.info("✅ ChromaDB initialized")
        
    except Exception as e:
        logger.warning(f"⚠️ ChromaDB initialization failed: {e}")

async def load_tariff_data():
    """Load tariff data from Excel file"""
    global tariff_data
    
    try:
        # Look for Excel file in multiple possible locations
        possible_paths = [
            Path("data/tariff_database_2025.xlsx"),  # Relative to current directory
            Path("../data/tariff_database_2025.xlsx"),  # Relative to backend directory
            Path("../../data/tariff_database_2025.xlsx"),  # Relative to app directory
        ]
        
        excel_path = None
        for path in possible_paths:
            if path.exists():
                excel_path = path
                break
        
        if not excel_path:
            logger.warning(f"❌ Excel file not found in any of these locations: {[str(p) for p in possible_paths]}")
            return
        
        logger.info(f"📊 Loading Excel data from {excel_path}")
        
        # Read the Excel file
        excel_data = pd.read_excel(excel_path, sheet_name=None, engine='openpyxl')
        
        # Find the main sheet with tariff data
        for sheet_name, df in excel_data.items():
            if len(df) > 1000:  # Assume main data sheet has many rows
                tariff_data = df
                logger.info(f"✅ Loaded {len(tariff_data)} tariff records from sheet '{sheet_name}'")
                break
        
        if tariff_data is not None:
            logger.info(f"📋 Available columns: {list(tariff_data.columns)}")
        
    except Exception as e:
        logger.warning(f"⚠️ Error loading tariff data: {e}")

def get_tariff_data():
    """Get loaded tariff data"""
    return tariff_data

def get_chroma_client():
    """Get ChromaDB client"""
    return chroma_client

def get_embedding_model():
    """Get embedding model"""
    return embedding_model 