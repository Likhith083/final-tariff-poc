"""
DataIngestionService for ATLAS Enterprise
Load and integrate tariff data and knowledge base into the system.
"""

import asyncio
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from core.config import settings
from core.logging import get_logger, log_business_event
from services.vector_service import vector_service
from models.document import Document
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.sql import func

logger = get_logger(__name__)


class DataIngestionService:
    """Service for loading and processing data files."""
    
    def __init__(self):
        """Initialize DataIngestionService."""
        self.data_path = Path("backend/data")
        self.knowledge_base_path = self.data_path / "knowledge_base"
        self.tariff_file = self.data_path / "tariff_database_2025.xlsx"
    
    async def load_tariff_data(self) -> Dict[str, Any]:
        """
        Load tariff data from Excel file.
        
        Returns:
            Dictionary containing tariff data
        """
        try:
            if not self.tariff_file.exists():
                logger.warning(f"Tariff file not found: {self.tariff_file}")
                return {"error": "Tariff file not found"}
            
            # Load Excel file
            logger.info(f"Loading tariff data from {self.tariff_file}")
            
            # Read all sheets
            excel_data = pd.read_excel(self.tariff_file, sheet_name=None)
            
            tariff_data = {}
            for sheet_name, df in excel_data.items():
                # Convert DataFrame to dict for easier processing
                tariff_data[sheet_name] = {
                    "columns": df.columns.tolist(),
                    "data": df.fillna("").to_dict("records"),
                    "row_count": len(df)
                }
                
                logger.info(f"Loaded sheet '{sheet_name}': {len(df)} rows, {len(df.columns)} columns")
            
            # Log business event
            log_business_event(
                "tariff_data_loaded",
                details={
                    "file_path": str(self.tariff_file),
                    "sheets_count": len(excel_data),
                    "total_rows": sum(len(df) for df in excel_data.values())
                }
            )
            
            return {
                "success": True,
                "sheets": list(tariff_data.keys()),
                "data": tariff_data,
                "summary": {
                    "total_sheets": len(tariff_data),
                    "total_rows": sum(sheet["row_count"] for sheet in tariff_data.values())
                }
            }
            
        except Exception as e:
            logger.error(f"Error loading tariff data: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def load_knowledge_base(self) -> Dict[str, Any]:
        """
        Load knowledge base from JSON files.
        
        Returns:
            Dictionary containing knowledge base data
        """
        try:
            knowledge_data = {}
            
            # Load main knowledge files from data directory
            main_files = [
                "tariff_management_kb.json",
                "srs_examples_kb.json", 
                "additional_knowledge.json",
                "adcvd_faq.json"
            ]
            
            for file_name in main_files:
                file_path = self.data_path / file_name
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        knowledge_data[file_name.replace('.json', '')] = data
                        logger.info(f"Loaded knowledge file: {file_name}")
            
            # Load files from knowledge_base subdirectory
            if self.knowledge_base_path.exists():
                for json_file in self.knowledge_base_path.glob("*.json"):
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            knowledge_data[json_file.stem] = data
                            logger.info(f"Loaded knowledge file: {json_file.name}")
                    except Exception as e:
                        logger.error(f"Error loading {json_file.name}: {e}")
            
            # Log business event
            log_business_event(
                "knowledge_base_loaded",
                details={
                    "files_count": len(knowledge_data),
                    "files": list(knowledge_data.keys())
                }
            )
            
            return {
                "success": True,
                "files": list(knowledge_data.keys()),
                "data": knowledge_data,
                "summary": {
                    "total_files": len(knowledge_data),
                    "total_entries": sum(
                        len(data) if isinstance(data, list) else 
                        len(data.get('entries', [])) if isinstance(data, dict) and 'entries' in data else
                        1 for data in knowledge_data.values()
                    )
                }
            }
            
        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def ingest_knowledge_to_vector_store(
        self,
        db: AsyncSession,
        knowledge_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Ingest knowledge base data into ChromaDB vector store.
        
        Args:
            db: Database session
            knowledge_data: Knowledge base data
            
        Returns:
            Ingestion results
        """
        try:
            await vector_service.initialize()
            
            ingested_count = 0
            total_chunks = 0
            
            for file_name, data in knowledge_data.items():
                try:
                    # Create or get document record
                    document = Document(
                        title=f"Knowledge Base: {file_name}",
                        document_type="knowledge_base",
                        file_path=f"data/{file_name}.json",
                        content_type="application/json",
                        tags=["knowledge_base", "tariff", "trade"],
                        metadata_={
                            "source": "knowledge_base",
                            "ingestion_date": datetime.utcnow().isoformat()
                        }
                    )
                    db.add(document)
                    await db.flush()  # Get the ID
                    
                    # Process data based on structure
                    texts_to_embed = []
                    metadatas = []
                    
                    if isinstance(data, list):
                        # List of items
                        for i, item in enumerate(data):
                            if isinstance(item, dict):
                                text = json.dumps(item, indent=2)
                                metadata = {
                                    "file_name": file_name,
                                    "item_index": i,
                                    "document_type": "knowledge_base"
                                }
                                if "question" in item:
                                    metadata["question"] = item["question"]
                                if "category" in item:
                                    metadata["category"] = item["category"]
                                    
                                texts_to_embed.append(text)
                                metadatas.append(metadata)
                    
                    elif isinstance(data, dict):
                        # Dictionary structure
                        if "entries" in data:
                            # Has entries field
                            for i, entry in enumerate(data["entries"]):
                                text = json.dumps(entry, indent=2)
                                metadata = {
                                    "file_name": file_name,
                                    "entry_index": i,
                                    "document_type": "knowledge_base"
                                }
                                texts_to_embed.append(text)
                                metadatas.append(metadata)
                        else:
                            # Direct dictionary
                            text = json.dumps(data, indent=2)
                            metadata = {
                                "file_name": file_name,
                                "document_type": "knowledge_base"
                            }
                            texts_to_embed.append(text)
                            metadatas.append(metadata)
                    
                    # Store in vector database
                    if texts_to_embed:
                        vector_ids = await vector_service.store_document_embeddings(
                            db, document.id, texts_to_embed, metadatas
                        )
                        
                        ingested_count += 1
                        total_chunks += len(vector_ids)
                        
                        logger.info(f"Ingested {file_name}: {len(vector_ids)} chunks")
                
                except Exception as e:
                    logger.error(f"Error ingesting {file_name}: {e}")
                    continue
            
            await db.commit()
            
            # Log business event
            log_business_event(
                "knowledge_base_ingested",
                details={
                    "files_ingested": ingested_count,
                    "total_chunks": total_chunks
                }
            )
            
            return {
                "success": True,
                "files_ingested": ingested_count,
                "total_chunks": total_chunks
            }
            
        except Exception as e:
            logger.error(f"Error ingesting knowledge to vector store: {e}")
            await db.rollback()
            return {
                "success": False,
                "error": str(e)
            }
    
    async def search_knowledge_base(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search the knowledge base using vector similarity.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            Search results
        """
        try:
            await vector_service.initialize()
            
            # Search with knowledge base filter
            results = await vector_service.similarity_search(
                query=query,
                top_k=top_k,
                filter_metadata={"document_type": "knowledge_base"}
            )
            
            # Format results for better readability
            formatted_results = []
            for result in results:
                formatted_result = {
                    "score": result["score"],
                    "content": result.get("text", ""),
                    "metadata": result.get("metadata", {}),
                    "file_name": result.get("metadata", {}).get("file_name", "unknown")
                }
                formatted_results.append(formatted_result)
            
            logger.info(f"Knowledge base search for '{query}' returned {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return []
    
    async def get_tariff_by_hts(self, hts_code: str) -> Dict[str, Any]:
        """
        Get tariff information by HTS code from loaded data.
        
        Args:
            hts_code: HTS code to search for
            
        Returns:
            Tariff information
        """
        try:
            # Load tariff data
            tariff_data = await self.load_tariff_data()
            
            if not tariff_data.get("success"):
                return {"error": "Failed to load tariff data"}
            
            # Search through all sheets for HTS code
            results = []
            
            for sheet_name, sheet_data in tariff_data["data"].items():
                for row in sheet_data["data"]:
                    # Look for HTS code in various possible column names
                    hts_columns = ["HTS", "HTS_Code", "HS_Code", "Code", "hts", "hts_code"]
                    
                    for col in hts_columns:
                        if col in row and str(row[col]).replace(".", "").replace(" ", "") == hts_code.replace(".", "").replace(" ", ""):
                            results.append({
                                "sheet": sheet_name,
                                "data": row,
                                "hts_code": str(row[col])
                            })
                            break
            
            return {
                "success": True,
                "hts_code": hts_code,
                "results": results,
                "found_count": len(results)
            }
            
        except Exception as e:
            logger.error(f"Error getting tariff by HTS {hts_code}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check data ingestion service health.
        
        Returns:
            Health check results
        """
        try:
            health_status = {
                "status": "healthy",
                "data_files": {
                    "tariff_excel": self.tariff_file.exists(),
                    "knowledge_base_dir": self.knowledge_base_path.exists()
                },
                "vector_store": False,
                "knowledge_files": []
            }
            
            # Check knowledge files
            if self.knowledge_base_path.exists():
                health_status["knowledge_files"] = [
                    f.name for f in self.knowledge_base_path.glob("*.json")
                ]
            
            # Check main knowledge files
            main_files = ["tariff_management_kb.json", "srs_examples_kb.json", "additional_knowledge.json", "adcvd_faq.json"]
            for file_name in main_files:
                if (self.data_path / file_name).exists():
                    health_status["knowledge_files"].append(file_name)
            
            # Check vector store
            try:
                await vector_service.initialize()
                stats = await vector_service.get_collection_stats()
                health_status["vector_store"] = True
                health_status["vector_count"] = stats.get("total_vector_count", 0)
            except Exception:
                health_status["vector_store"] = False
            
            return health_status
            
        except Exception as e:
            logger.error(f"Data ingestion health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }


# Global instance
data_ingestion_service = DataIngestionService() 