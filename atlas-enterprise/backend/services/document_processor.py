"""
DocumentProcessor for ATLAS Enterprise
Document ingestion, processing, and embedding generation.
"""

import asyncio
import os
from typing import List, Dict, Any, Optional, BinaryIO
from datetime import datetime
from pathlib import Path
import mimetypes
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..core.logging import get_logger, log_business_event
from ..models.document import Document, DocumentEmbedding
from .vector_service import vector_service

logger = get_logger(__name__)


class DocumentProcessor:
    """Service for processing and indexing documents."""
    
    def __init__(self):
        """Initialize document processor."""
        self.supported_types = {
            'text/plain': self._process_text,
            'application/pdf': self._process_pdf,
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': self._process_docx,
            'text/csv': self._process_csv,
            'application/json': self._process_json
        }
    
    async def process_document(
        self,
        db: AsyncSession,
        file_content: bytes,
        filename: str,
        document_type: str = "general",
        title: Optional[str] = None,
        tags: Optional[List[str]] = None,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process a document and create embeddings.
        
        Args:
            db: Database session
            file_content: File content as bytes
            filename: Original filename
            document_type: Type of document
            title: Document title (defaults to filename)
            tags: Document tags
            user_id: User who uploaded the document
            
        Returns:
            Processing result with document ID and stats
        """
        try:
            # Determine file type
            mime_type, _ = mimetypes.guess_type(filename)
            if not mime_type or mime_type not in self.supported_types:
                return {
                    "success": False,
                    "error": f"Unsupported file type: {mime_type}",
                    "error_code": "UNSUPPORTED_FILE_TYPE"
                }
            
            # Save file to storage
            file_path = await self._save_file(file_content, filename)
            
            # Create document record
            document = Document(
                title=title or filename,
                document_type=document_type,
                file_path=str(file_path),
                file_size=len(file_content),
                mime_type=mime_type,
                tags=tags or [],
                uploaded_by=user_id,
                processing_status="processing"
            )
            
            db.add(document)
            await db.commit()
            await db.refresh(document)
            
            # Extract text content
            text_content = await self.supported_types[mime_type](file_content)
            
            if not text_content:
                document.processing_status = "failed"
                document.error_message = "No text content extracted"
                await db.commit()
                
                return {
                    "success": False,
                    "error": "No text content could be extracted",
                    "error_code": "NO_TEXT_CONTENT"
                }
            
            # Split text into chunks
            chunks = vector_service.split_text(text_content)
            
            # Create metadata for each chunk
            chunk_metadatas = []
            for i, chunk in enumerate(chunks):
                metadata = {
                    "document_type": document_type,
                    "filename": filename,
                    "chunk_size": len(chunk),
                    "tags": tags or []
                }
                chunk_metadatas.append(metadata)
            
            # Store embeddings
            vector_ids = await vector_service.store_document_embeddings(
                db, document.id, chunks, chunk_metadatas
            )
            
            # Update document status
            document.processing_status = "completed"
            document.content_preview = text_content[:500]  # First 500 chars
            document.chunk_count = len(chunks)
            await db.commit()
            
            # Log business event
            log_business_event(
                "document_processed",
                user_id=str(user_id) if user_id else None,
                details={
                    "document_id": document.id,
                    "filename": filename,
                    "document_type": document_type,
                    "file_size": len(file_content),
                    "chunk_count": len(chunks),
                    "vector_count": len(vector_ids)
                }
            )
            
            logger.info(f"Processed document {filename}: {len(chunks)} chunks, {len(vector_ids)} vectors")
            
            return {
                "success": True,
                "document_id": document.id,
                "filename": filename,
                "text_length": len(text_content),
                "chunk_count": len(chunks),
                "vector_count": len(vector_ids),
                "processing_time": "completed"
            }
            
        except Exception as e:
            logger.error(f"Error processing document {filename}: {e}")
            
            # Update document status if it exists
            if 'document' in locals():
                document.processing_status = "failed"
                document.error_message = str(e)
                await db.commit()
            
            return {
                "success": False,
                "error": str(e),
                "error_code": "PROCESSING_ERROR"
            }
    
    async def _save_file(self, file_content: bytes, filename: str) -> Path:
        """Save file to storage directory."""
        # Create upload directory if it doesn't exist
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_filename = "".join(c for c in filename if c.isalnum() or c in "._-")
        unique_filename = f"{timestamp}_{safe_filename}"
        
        file_path = upload_dir / unique_filename
        
        # Write file
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        return file_path
    
    async def _process_text(self, file_content: bytes) -> str:
        """Process plain text file."""
        try:
            return file_content.decode('utf-8')
        except UnicodeDecodeError:
            # Try different encodings
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    return file_content.decode(encoding)
                except UnicodeDecodeError:
                    continue
            raise ValueError("Could not decode text file")
    
    async def _process_pdf(self, file_content: bytes) -> str:
        """Process PDF file (placeholder - requires PyPDF2 or similar)."""
        # In production, you would use PyPDF2, pdfplumber, or similar
        logger.warning("PDF processing not implemented - returning placeholder")
        return "PDF content extraction not implemented. Please implement using PyPDF2 or pdfplumber."
    
    async def _process_docx(self, file_content: bytes) -> str:
        """Process DOCX file (placeholder - requires python-docx)."""
        # In production, you would use python-docx
        logger.warning("DOCX processing not implemented - returning placeholder")
        return "DOCX content extraction not implemented. Please implement using python-docx."
    
    async def _process_csv(self, file_content: bytes) -> str:
        """Process CSV file."""
        try:
            import csv
            import io
            
            text_content = file_content.decode('utf-8')
            csv_reader = csv.reader(io.StringIO(text_content))
            
            # Convert CSV to text format
            rows = []
            for row in csv_reader:
                rows.append(" | ".join(row))
            
            return "\n".join(rows)
            
        except Exception as e:
            logger.error(f"Error processing CSV: {e}")
            return ""
    
    async def _process_json(self, file_content: bytes) -> str:
        """Process JSON file."""
        try:
            import json
            
            json_data = json.loads(file_content.decode('utf-8'))
            
            # Convert JSON to readable text
            return json.dumps(json_data, indent=2)
            
        except Exception as e:
            logger.error(f"Error processing JSON: {e}")
            return ""
    
    async def delete_document(
        self,
        db: AsyncSession,
        document_id: int
    ) -> bool:
        """
        Delete a document and its embeddings.
        
        Args:
            db: Database session
            document_id: Document ID to delete
            
        Returns:
            True if successful
        """
        try:
            # Get document
            from sqlalchemy import select
            stmt = select(Document).where(Document.id == document_id)
            result = await db.execute(stmt)
            document = result.scalar_one_or_none()
            
            if not document:
                return False
            
            # Delete embeddings from vector store
            await vector_service.delete_document_embeddings(db, document_id)
            
            # Delete file from storage
            if document.file_path and os.path.exists(document.file_path):
                os.remove(document.file_path)
            
            # Delete document record
            await db.delete(document)
            await db.commit()
            
            logger.info(f"Deleted document {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            await db.rollback()
            return False
    
    async def get_processing_stats(self, db: AsyncSession) -> Dict[str, Any]:
        """Get document processing statistics."""
        try:
            from sqlalchemy import select, func
            
            # Total documents
            total_stmt = select(func.count(Document.id))
            total_result = await db.execute(total_stmt)
            total_documents = total_result.scalar() or 0
            
            # Documents by status
            status_stmt = select(
                Document.processing_status,
                func.count(Document.id)
            ).group_by(Document.processing_status)
            status_result = await db.execute(status_stmt)
            status_counts = {row[0]: row[1] for row in status_result}
            
            # Documents by type
            type_stmt = select(
                Document.document_type,
                func.count(Document.id)
            ).group_by(Document.document_type)
            type_result = await db.execute(type_stmt)
            type_counts = {row[0]: row[1] for row in type_result}
            
            # Total embeddings
            embedding_stmt = select(func.count(DocumentEmbedding.id))
            embedding_result = await db.execute(embedding_stmt)
            total_embeddings = embedding_result.scalar() or 0
            
            return {
                "total_documents": total_documents,
                "status_breakdown": status_counts,
                "type_breakdown": type_counts,
                "total_embeddings": total_embeddings,
                "supported_types": list(self.supported_types.keys())
            }
            
        except Exception as e:
            logger.error(f"Error getting processing stats: {e}")
            return {}


# Global instance
document_processor = DocumentProcessor() 