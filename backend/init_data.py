#!/usr/bin/env python3
"""
Data initialization script for Tariff AI Backend
"""

import asyncio
import os
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.core.database import Base
from app.services.hts_service import HTSService
from app.services.vector_store import VectorStoreService

async def init_database():
    """Initialize database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")

async def init_hts_data():
    """Initialize HTS data from Excel file"""
    print("Loading HTS data from Excel...")
    try:
        db = SessionLocal()
        hts_service = HTSService()
        imported_count = await hts_service.import_from_excel(db)
        print(f"✅ Imported {imported_count} HTS records")
        db.close()
    except Exception as e:
        print(f"⚠️  HTS data import failed: {str(e)}")
        print("   This is normal if the Excel file is not available yet")

async def init_knowledge_base():
    """Initialize knowledge base from reference data"""
    print("Loading knowledge base...")
    try:
        vector_store = VectorStoreService()
        knowledge_base_path = "./data/adcvd_faq.json"
        loaded_count = await vector_store.load_knowledge_base(knowledge_base_path)
        print(f"✅ Loaded {loaded_count} documents into knowledge base")
    except Exception as e:
        print(f"⚠️  Knowledge base initialization failed: {str(e)}")
        print("   This is normal if the reference data is not available yet")

async def main():
    """Main initialization function"""
    print("🚀 Initializing Tariff AI Backend...")
    print("=" * 50)
    
    await init_database()
    await init_hts_data()
    await init_knowledge_base()
    
    print("=" * 50)
    print("✅ Initialization complete!")
    print("\nYou can now start the backend with:")
    print("   python main.py")
    print("   or")
    print("   uvicorn main:app --reload")

if __name__ == "__main__":
    asyncio.run(main()) 