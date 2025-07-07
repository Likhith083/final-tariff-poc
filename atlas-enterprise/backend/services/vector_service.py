"""
VectorService for ATLAS Enterprise
ChromaDB integration for document search and AI capabilities.
"""

import asyncio
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import chromadb
from chromadb.config import Settings
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document as LangchainDocument

from core.config import settings
from core.logging import get_logger, log_business_event
from models.document import Document, DocumentEmbedding
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

logger = get_logger(__name__)


class VectorService:
    """Service for vector operations and document embeddings using ChromaDB."""
    
    def __init__(self):
        """Initialize VectorService with ChromaDB."""
        self.embeddings = None
        self.chroma_client = None
        self.collection = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize ChromaDB connection and embeddings."""
        if self._initialized:
            return
        
        try:
            # Ensure data directory exists
            os.makedirs(settings.chroma_db_path, exist_ok=True)
            
            # Initialize ChromaDB client
            self.chroma_client = chromadb.PersistentClient(
                path=settings.chroma_db_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self.chroma_client.get_or_create_collection(
                name=settings.chroma_collection_name,
                metadata={"description": "ATLAS Enterprise document embeddings"}
            )
            
            # Initialize HuggingFace embeddings (free alternative to OpenAI)
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            
            self._initialized = True
            logger.info("VectorService initialized successfully with ChromaDB")
            
        except Exception as e:
            logger.error(f"Failed to initialize VectorService: {e}")
            raise
    
    async def create_embeddings(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> List[List[float]]:
        """
        Create embeddings for a list of texts.
        
        Args:
            texts: List of texts to embed
            metadatas: Optional metadata for each text
            
        Returns:
            List of embedding vectors
        """
        await self.initialize()
        
        try:
            # Create embeddings using HuggingFace
            embeddings = await asyncio.to_thread(
                self.embeddings.embed_documents, texts
            )
            
            logger.info(f"Created {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            raise
    
    async def store_document_embeddings(
        self,
        db: AsyncSession,
        document_id: int,
        text_chunks: List[str],
        chunk_metadatas: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Store document embeddings in both database and ChromaDB.
        
        Args:
            db: Database session
            document_id: Document ID
            text_chunks: List of text chunks
            chunk_metadatas: Metadata for each chunk
            
        Returns:
            List of vector IDs
        """
        await self.initialize()
        
        try:
            # Create embeddings
            embeddings = await self.create_embeddings(text_chunks)
            
            # Prepare data for ChromaDB
            vector_ids = []
            chroma_ids = []
            chroma_embeddings = []
            chroma_metadatas = []
            chroma_documents = []
            
            for i, (chunk, embedding, metadata) in enumerate(
                zip(text_chunks, embeddings, chunk_metadatas)
            ):
                vector_id = f"doc_{document_id}_chunk_{i}_{datetime.utcnow().timestamp()}"
                vector_ids.append(vector_id)
                
                # Prepare ChromaDB data
                chroma_ids.append(vector_id)
                chroma_embeddings.append(embedding)
                chroma_metadatas.append({
                    **metadata,
                    "document_id": document_id,
                    "chunk_index": i,
                    "timestamp": datetime.utcnow().isoformat()
                })
                chroma_documents.append(chunk[:1000])  # ChromaDB stores document text
                
                # Store in database
                doc_embedding = DocumentEmbedding(
                    document_id=document_id,
                    vector_id=vector_id,
                    chunk_index=i,
                    text_content=chunk,
                    embedding_model="sentence-transformers/all-MiniLM-L6-v2",
                    metadata=metadata
                )
                db.add(doc_embedding)
            
            # Add to ChromaDB collection
            await asyncio.to_thread(
                self.collection.add,
                ids=chroma_ids,
                embeddings=chroma_embeddings,
                metadatas=chroma_metadatas,
                documents=chroma_documents
            )
            
            # Commit database changes
            await db.commit()
            
            logger.info(f"Stored {len(vector_ids)} embeddings for document {document_id}")
            
            # Log business event
            log_business_event(
                "document_embeddings_created",
                details={
                    "document_id": document_id,
                    "chunk_count": len(vector_ids),
                    "model": "sentence-transformers/all-MiniLM-L6-v2"
                }
            )
            
            return vector_ids
            
        except Exception as e:
            logger.error(f"Error storing document embeddings: {e}")
            await db.rollback()
            raise
    
    async def similarity_search(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Perform similarity search in ChromaDB.
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
            include_metadata: Whether to include metadata in results
            
        Returns:
            List of search results with scores and metadata
        """
        await self.initialize()
        
        try:
            # Create query embedding
            query_embedding = await asyncio.to_thread(
                self.embeddings.embed_query, query
            )
            
            # Search in ChromaDB
            search_results = await asyncio.to_thread(
                self.collection.query,
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filter_metadata,
                include=['metadatas', 'documents', 'distances']
            )
            
            # Format results
            results = []
            if search_results['ids'] and search_results['ids'][0]:
                for i, doc_id in enumerate(search_results['ids'][0]):
                    result = {
                        "id": doc_id,
                        "score": 1.0 - search_results['distances'][0][i],  # Convert distance to similarity
                        "metadata": search_results['metadatas'][0][i] if include_metadata else {},
                        "text": search_results['documents'][0][i] if search_results['documents'] else ""
                    }
                    results.append(result)
            
            logger.info(f"Similarity search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            raise
    
    async def search_documents(
        self,
        db: AsyncSession,
        query: str,
        document_types: Optional[List[str]] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search documents with enhanced metadata from database.
        
        Args:
            db: Database session
            query: Search query
            document_types: Optional filter by document types
            top_k: Number of results to return
            
        Returns:
            List of document search results with full metadata
        """
        try:
            # Build filter
            filter_metadata = {}
            if document_types:
                filter_metadata["document_type"] = {"$in": document_types}
            
            # Perform similarity search
            vector_results = await self.similarity_search(
                query, top_k, filter_metadata
            )
            
            # Get document IDs from results
            document_ids = [
                result["metadata"].get("document_id") 
                for result in vector_results 
                if result["metadata"].get("document_id")
            ]
            
            # Fetch full document metadata from database
            if document_ids:
                stmt = select(Document).where(Document.id.in_(document_ids))
                db_result = await db.execute(stmt)
                documents = {doc.id: doc for doc in db_result.scalars().all()}
            else:
                documents = {}
            
            # Combine results
            enhanced_results = []
            for result in vector_results:
                document_id = result["metadata"].get("document_id")
                document = documents.get(document_id)
                
                enhanced_result = {
                    **result,
                    "document": {
                        "id": document.id,
                        "title": document.title,
                        "document_type": document.document_type,
                        "file_path": document.file_path,
                        "created_at": document.created_at.isoformat(),
                        "tags": document.tags
                    } if document else None,
                    "text_content": result.get("text", "")
                }
                enhanced_results.append(enhanced_result)
            
            logger.info(f"Enhanced document search returned {len(enhanced_results)} results")
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Error in document search: {e}")
            raise
    
    async def delete_document_embeddings(
        self,
        db: AsyncSession,
        document_id: int
    ) -> bool:
        """
        Delete all embeddings for a document.
        
        Args:
            db: Database session
            document_id: Document ID
            
        Returns:
            True if successful
        """
        await self.initialize()
        
        try:
            # Get vector IDs from database
            stmt = select(DocumentEmbedding.vector_id).where(
                DocumentEmbedding.document_id == document_id
            )
            result = await db.execute(stmt)
            vector_ids = [row[0] for row in result.fetchall()]
            
            if vector_ids:
                # Delete from ChromaDB
                await asyncio.to_thread(self.collection.delete, ids=vector_ids)
                
                # Delete from database
                stmt = select(DocumentEmbedding).where(
                    DocumentEmbedding.document_id == document_id
                )
                result = await db.execute(stmt)
                embeddings = result.scalars().all()
                
                for embedding in embeddings:
                    await db.delete(embedding)
                
                await db.commit()
                
                logger.info(f"Deleted {len(vector_ids)} embeddings for document {document_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document embeddings: {e}")
            await db.rollback()
            return False
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get ChromaDB collection statistics.
        
        Returns:
            Collection statistics
        """
        await self.initialize()
        
        try:
            count = await asyncio.to_thread(self.collection.count)
            
            return {
                "total_vector_count": count,
                "collection_name": settings.chroma_collection_name,
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
                "database_path": settings.chroma_db_path
            }
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}
    
    def split_text(
        self,
        text: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> List[str]:
        """
        Split text into chunks for embedding.
        
        Args:
            text: Text to split
            chunk_size: Size of each chunk
            chunk_overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
        
        chunks = text_splitter.split_text(text)
        logger.info(f"Split text into {len(chunks)} chunks")
        return chunks


# Global instance
vector_service = VectorService() 