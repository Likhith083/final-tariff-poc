from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import engine, AsyncSessionLocal
from app.db.models import Base
from app.services.chroma_service import ChromaService
from app.services.hts_service import HTSService
from loguru import logger
import pandas as pd
import json
from pathlib import Path
from app.core.config import settings

async def init_database():
    """Initialize database tables and load initial data"""
    try:
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database tables created successfully")
        
        # Initialize ChromaDB
        chroma_service = ChromaService()
        await chroma_service.initialize()
        logger.info("ChromaDB initialized successfully")
        
        # Load initial HTS data if not exists
        await load_initial_data()
        
        logger.info("Database initialization completed")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

async def load_initial_data():
    """Load initial data from Excel and JSON files"""
    try:
        # Load HTS data from Excel
        if Path(settings.TARIFF_DATABASE_PATH).exists():
            hts_service = HTSService()
            await hts_service.load_tariff_data()
            logger.info("HTS data loaded successfully")
        else:
            logger.warning(f"Tariff database file not found: {settings.TARIFF_DATABASE_PATH}")
        
        # Load AD/CVD FAQ data
        if Path(settings.ADCVD_FAQ_PATH).exists():
            await load_adcvd_faq()
            logger.info("AD/CVD FAQ data loaded successfully")
        else:
            logger.warning(f"AD/CVD FAQ file not found: {settings.ADCVD_FAQ_PATH}")
            
    except Exception as e:
        logger.error(f"Failed to load initial data: {e}")

async def load_adcvd_faq():
    """Load AD/CVD FAQ data into ChromaDB"""
    try:
        with open(settings.ADCVD_FAQ_PATH, 'r') as f:
            faq_data = json.load(f)
        
        chroma_service = ChromaService()
        collection = await chroma_service.get_collection("adcvd_faq")
        
        # Prepare documents for ChromaDB
        documents = []
        metadatas = []
        ids = []
        
        for i, faq in enumerate(faq_data.get("faqs", [])):
            question = faq.get("question", "")
            answer = faq.get("answer", "")
            
            # Combine question and answer for better search
            content = f"Question: {question}\nAnswer: {answer}"
            
            documents.append(content)
            metadatas.append({
                "question": question,
                "answer": answer,
                "type": "adcvd_faq"
            })
            ids.append(f"faq_{i}")
        
        if documents:
            await collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Loaded {len(documents)} AD/CVD FAQ entries")
            
    except Exception as e:
        logger.error(f"Failed to load AD/CVD FAQ: {e}")

async def reset_database():
    """Reset database (for development/testing)"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database reset completed")
        
    except Exception as e:
        logger.error(f"Database reset failed: {e}")
        raise
