"""
Initialize the database with default data
"""
import asyncio
from sqlalchemy.orm import Session
from app.core.database import engine, SessionLocal
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage
from app.services.vector_store import VectorStoreService
from passlib.context import CryptContext
import os
import json

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_default_user(db: Session):
    """Create a default user if none exists"""
    user = db.query(User).first()
    if not user:
        print("Creating default user...")
        default_user = User(
            email="admin@tariffai.com",
            username="admin",
            full_name="Default Admin",
            hashed_password=pwd_context.hash("admin123"),
            is_active=True,
            is_superuser=True
        )
        db.add(default_user)
        db.commit()
        db.refresh(default_user)
        print(f"Created default user with ID: {default_user.id}")
        return default_user
    else:
        print(f"User already exists with ID: {user.id}")
        return user

async def initialize_knowledge_base():
    """Initialize the knowledge base with tariff management data"""
    print("Initializing Tariff Management knowledge base...")
    vector_store = VectorStoreService()
    
    # Clear existing collection to start fresh
    await vector_store.clear_collection()
    
    total_loaded = 0
    
    # Load FAQ data
    faq_path = "./data/adcvd_faq.json"
    if os.path.exists(faq_path):
        try:
            loaded_count = await vector_store.load_knowledge_base(faq_path)
            print(f"Loaded {loaded_count} FAQ entries")
            total_loaded += loaded_count
        except Exception as e:
            print(f"Error loading FAQ data: {e}")
    
    # Load tariff management knowledge base
    tariff_kb_path = "./data/tariff_management_kb.json"
    if os.path.exists(tariff_kb_path):
        try:
            loaded_count = await vector_store.load_knowledge_base(tariff_kb_path)
            print(f"Loaded {loaded_count} tariff management entries")
            total_loaded += loaded_count
        except Exception as e:
            print(f"Error loading tariff knowledge base: {e}")
    
    # Load SRS examples knowledge base
    srs_kb_path = "./data/srs_examples_kb.json"
    if os.path.exists(srs_kb_path):
        try:
            loaded_count = await vector_store.load_knowledge_base(srs_kb_path)
            print(f"Loaded {loaded_count} SRS example entries")
            total_loaded += loaded_count
        except Exception as e:
            print(f"Error loading SRS examples: {e}")
    
    # Load additional knowledge if available
    additional_path = "./data/additional_knowledge.json"
    if os.path.exists(additional_path):
        try:
            loaded_count = await vector_store.load_knowledge_base(additional_path)
            print(f"Loaded {loaded_count} additional knowledge entries")
            total_loaded += loaded_count
        except Exception as e:
            print(f"Error loading additional knowledge: {e}")
    
    # Load knowledge base folder if it exists
    kb_folder = "./data/knowledge_base"
    if os.path.exists(kb_folder):
        try:
            loaded_count = await vector_store.load_knowledge_base_folder(kb_folder)
            print(f"Loaded {loaded_count} entries from knowledge base folder")
            total_loaded += loaded_count
        except Exception as e:
            print(f"Error loading knowledge base folder: {e}")
    
    # Check final collection stats
    stats = await vector_store.get_collection_stats()
    print(f"Total knowledge base entries loaded: {total_loaded}")
    print(f"Final knowledge base stats: {stats}")
    
    return total_loaded

def main():
    """Main initialization function"""
    print("Starting database initialization...")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Create default user
        user = create_default_user(db)
        
        # Initialize knowledge base
        asyncio.run(initialize_knowledge_base())
        
        print("Database initialization completed successfully!")
        
    except Exception as e:
        print(f"Error during initialization: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
