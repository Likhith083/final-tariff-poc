"""
Database initialization and management for TariffAI
Handles ChromaDB setup and data loading from the original projects.
"""

import os
import logging
import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict, Any
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer

from app.core.config import settings

logger = logging.getLogger(__name__)

# Global variables
chroma_client: Optional[chromadb.PersistentClient] = None
chroma_collection: Optional[chromadb.Collection] = None
embedding_model: Optional[SentenceTransformer] = None
tariff_data: Optional[pd.DataFrame] = None


async def init_database() -> None:
    """Initialize database and load tariff data."""
    global chroma_client, chroma_collection, embedding_model, tariff_data
    
    try:
        # Create data directory if it doesn't exist
        data_dir = Path(settings.chroma_db_path)
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB
        chroma_client = chromadb.PersistentClient(
            path=settings.chroma_db_path,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize embedding model
        embedding_model = SentenceTransformer(settings.embedding_model_name)
        logger.info(f"✅ Embedding model '{settings.embedding_model_name}' loaded")
        
        # Load tariff data
        tariff_data = await load_tariff_data()
        
        # Initialize ChromaDB collection
        await init_chroma_collection()
        
        logger.info("✅ Database initialization complete")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise


async def load_tariff_data() -> Optional[pd.DataFrame]:
    """Load tariff data from Excel file."""
    try:
        excel_path = Path(settings.excel_data_path)
        
        if not excel_path.exists():
            logger.warning(f"⚠️ Excel file not found: {excel_path}")
            logger.info("Creating sample data for testing...")
            return create_sample_data()
        
        # Load Excel data
        df = pd.read_excel(excel_path)
        logger.info(f"✅ Loaded {len(df)} tariff records from {excel_path}")
        
        # Basic data cleaning
        df = clean_tariff_data(df)
        
        return df
        
    except Exception as e:
        logger.error(f"❌ Error loading tariff data: {e}")
        logger.info("Creating sample data for testing...")
        return create_sample_data()


def clean_tariff_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and prepare tariff data."""
    try:
        # Remove rows with missing HTS codes
        df = df.dropna(subset=['hts8'])
        
        # Clean HTS codes (remove dots, ensure 10 digits)
        df['hts8'] = df['hts8'].astype(str).str.replace('.', '').str.zfill(10)
        
        # Clean descriptions
        df['brief_description'] = df['brief_description'].fillna('').astype(str)
        
        # Convert numeric columns
        numeric_columns = [
            'mfn_ad_val_rate this is the general tariff rate',
            'mfn_specific_rate',
            'mfn_other_rate'
        ]
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        logger.info(f"✅ Cleaned {len(df)} tariff records")
        return df
        
    except Exception as e:
        logger.error(f"❌ Error cleaning tariff data: {e}")
        return df


def create_sample_data() -> pd.DataFrame:
    """Create sample tariff data for testing."""
    sample_data = [
        # Steel products
        {
            'hts8': '7304410000',
            'brief_description': 'Stainless steel pipes and tubes, seamless',
            'mfn_ad_val_rate this is the general tariff rate': 2.5,
            'mfn_specific_rate': 0.0,
            'mfn_other_rate': 0.0
        },
        {
            'hts8': '7304490000',
            'brief_description': 'Stainless steel pipes and tubes, welded',
            'mfn_ad_val_rate this is the general tariff rate': 3.2,
            'mfn_specific_rate': 0.0,
            'mfn_other_rate': 0.0
        },
        {
            'hts8': '7306300000',
            'brief_description': 'Steel pipes and tubes, welded, circular',
            'mfn_ad_val_rate this is the general tariff rate': 4.8,
            'mfn_specific_rate': 0.0,
            'mfn_other_rate': 0.0
        },
        {
            'hts8': '7210300000',
            'brief_description': 'Steel sheets, hot-rolled, flat-rolled',
            'mfn_ad_val_rate this is the general tariff rate': 5.2,
            'mfn_specific_rate': 0.0,
            'mfn_other_rate': 0.0
        },
        {
            'hts8': '7210490000',
            'brief_description': 'Steel sheets, cold-rolled, flat-rolled',
            'mfn_ad_val_rate this is the general tariff rate': 6.1,
            'mfn_specific_rate': 0.0,
            'mfn_other_rate': 0.0
        },
        {
            'hts8': '7225500000',
            'brief_description': 'Steel wire, flat-rolled products',
            'mfn_ad_val_rate this is the general tariff rate': 3.8,
            'mfn_specific_rate': 0.0,
            'mfn_other_rate': 0.0
        },
        {
            'hts8': '7308900000',
            'brief_description': 'Steel structures and parts of structures',
            'mfn_ad_val_rate this is the general tariff rate': 4.5,
            'mfn_specific_rate': 0.0,
            'mfn_other_rate': 0.0
        },
        {
            'hts8': '7318150000',
            'brief_description': 'Steel screws, bolts and nuts',
            'mfn_ad_val_rate this is the general tariff rate': 5.8,
            'mfn_specific_rate': 0.0,
            'mfn_other_rate': 0.0
        },
        {
            'hts8': '7326900000',
            'brief_description': 'Steel articles, household and sanitary',
            'mfn_ad_val_rate this is the general tariff rate': 7.2,
            'mfn_specific_rate': 0.0,
            'mfn_other_rate': 0.0
        },
        {
            'hts8': '7304290000',
            'brief_description': 'Steel tubes and pipes, seamless, other',
            'mfn_ad_val_rate this is the general tariff rate': 3.9,
            'mfn_specific_rate': 0.0,
            'mfn_other_rate': 0.0
        },
        # Other products for variety
        {
            'hts8': '8517120000',
            'brief_description': 'Mobile phones, smartphones',
            'mfn_ad_val_rate this is the general tariff rate': 0.0,
            'mfn_specific_rate': 0.0,
            'mfn_other_rate': 0.0
        },
        {
            'hts8': '6204430000',
            'brief_description': 'Women\'s dresses, synthetic fibers',
            'mfn_ad_val_rate this is the general tariff rate': 16.0,
            'mfn_specific_rate': 0.0,
            'mfn_other_rate': 0.0
        },
        {
            'hts8': '8471300000',
            'brief_description': 'Portable computers, laptops',
            'mfn_ad_val_rate this is the general tariff rate': 0.0,
            'mfn_specific_rate': 0.0,
            'mfn_other_rate': 0.0
        },
        {
            'hts8': '9503000000',
            'brief_description': 'Toys and games, not specified elsewhere',
            'mfn_ad_val_rate this is the general tariff rate': 0.0,
            'mfn_specific_rate': 0.0,
            'mfn_other_rate': 0.0
        }
    ]
    
    df = pd.DataFrame(sample_data)
    logger.info(f"✅ Created {len(df)} sample tariff records")
    return df


async def init_chroma_collection() -> None:
    """Initialize ChromaDB collection for vector search."""
    global chroma_client, chroma_collection, tariff_data
    
    if not chroma_client or tariff_data is None:
        logger.error("❌ ChromaDB client or tariff data not initialized")
        return
    
    try:
        collection_name = "hts_search"
        
        # Try to get existing collection
        try:
            chroma_collection = chroma_client.get_collection(name=collection_name)
            logger.info(f"✅ Loaded existing collection: {collection_name}")
        except:
            # Create new collection
            chroma_collection = chroma_client.create_collection(
                name=collection_name,
                metadata={"description": "HTS code search collection"}
            )
            logger.info(f"✅ Created new collection: {collection_name}")
        
        # Index data if collection is empty
        if chroma_collection.count() == 0:
            await index_tariff_data()
        
        logger.info(f"✅ ChromaDB collection ready with {chroma_collection.count()} documents")
        
    except Exception as e:
        logger.error(f"❌ Error initializing ChromaDB collection: {e}")
        raise


async def index_tariff_data() -> None:
    """Index tariff data in ChromaDB for vector search."""
    global chroma_collection, tariff_data, embedding_model
    
    if not chroma_collection or tariff_data is None or embedding_model is None:
        logger.error("❌ Required components not initialized for indexing")
        return
    
    try:
        # Prepare data for indexing
        documents = []
        metadatas = []
        ids = []
        
        for idx, row in tariff_data.iterrows():
            hts_code = str(row.get('hts8', '')).strip()
            description = str(row.get('brief_description', '')).strip()
            
            if hts_code and hts_code != 'nan' and description and description != 'nan':
                # Create document text
                doc_text = f"HTS Code: {hts_code}. Description: {description}"
                
                documents.append(doc_text)
                metadatas.append({
                    "hts_code": hts_code,
                    "description": description,
                    "tariff_rate": float(row.get('mfn_ad_val_rate this is the general tariff rate', 0)),
                    "specific_rate": float(row.get('mfn_specific_rate', 0)),
                    "other_rate": float(row.get('mfn_other_rate', 0))
                })
                ids.append(f"doc_{idx}")
        
        # Add documents in batches
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i + batch_size]
            batch_metadatas = metadatas[i:i + batch_size]
            batch_ids = ids[i:i + batch_size]
            
            chroma_collection.add(
                documents=batch_docs,
                metadatas=batch_metadatas,
                ids=batch_ids
            )
        
        logger.info(f"✅ Indexed {len(documents)} documents in ChromaDB")
        
    except Exception as e:
        logger.error(f"❌ Error indexing tariff data: {e}")
        raise


def get_chroma_collection() -> Optional[chromadb.Collection]:
    """Get the ChromaDB collection."""
    return chroma_collection


def get_embedding_model() -> Optional[SentenceTransformer]:
    """Get the embedding model."""
    return embedding_model


def get_tariff_data() -> Optional[pd.DataFrame]:
    """Get the tariff data."""
    return tariff_data 