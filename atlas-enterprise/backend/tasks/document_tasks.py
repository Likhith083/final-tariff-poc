"""
Document Processing Tasks for ATLAS Enterprise
Background tasks for document processing and cleanup.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any
from celery import current_task
from sqlalchemy import select, and_

from .celery_app import celery_app
from ..core.database import get_async_session
from ..core.logging import get_logger
from ..services.document_processor import document_processor
from ..models.document import Document

logger = get_logger(__name__)


@celery_app.task(bind=True, name="backend.tasks.document_tasks.process_document_async")
def process_document_async(
    self,
    file_content_base64: str,
    filename: str,
    document_type: str = "general",
    title: str = None,
    tags: list = None,
    user_id: int = None
) -> Dict[str, Any]:
    """
    Process document asynchronously in background.
    
    Args:
        file_content_base64: Base64 encoded file content
        filename: Original filename
        document_type: Type of document
        title: Document title
        tags: Document tags
        user_id: User who uploaded the document
        
    Returns:
        Processing result
    """
    try:
        import base64
        
        # Update task status
        current_task.update_state(
            state="PROCESSING",
            meta={"status": "Decoding file content", "progress": 10}
        )
        
        # Decode file content
        file_content = base64.b64decode(file_content_base64)
        
        # Update task status
        current_task.update_state(
            state="PROCESSING", 
            meta={"status": "Processing document", "progress": 30}
        )
        
        # Process document using async session
        async def _process():
            async with get_async_session() as db:
                result = await document_processor.process_document(
                    db, file_content, filename, document_type, title, tags, user_id
                )
                return result
        
        # Run async processing
        result = asyncio.run(_process())
        
        # Update final status
        if result["success"]:
            current_task.update_state(
                state="SUCCESS",
                meta={
                    "status": "Document processed successfully",
                    "progress": 100,
                    "result": result
                }
            )
        else:
            current_task.update_state(
                state="FAILURE",
                meta={
                    "status": f"Processing failed: {result.get('error', 'Unknown error')}",
                    "progress": 100,
                    "error": result.get("error")
                }
            )
        
        logger.info(f"Document processing task completed for {filename}")
        return result
        
    except Exception as e:
        logger.error(f"Error in document processing task: {e}")
        current_task.update_state(
            state="FAILURE",
            meta={"status": f"Task failed: {str(e)}", "error": str(e)}
        )
        return {"success": False, "error": str(e)}


@celery_app.task(name="backend.tasks.document_tasks.cleanup_old_documents")
def cleanup_old_documents(days_old: int = 90) -> Dict[str, Any]:
    """
    Clean up old documents and their embeddings.
    
    Args:
        days_old: Delete documents older than this many days
        
    Returns:
        Cleanup results
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        async def _cleanup():
            async with get_async_session() as db:
                # Find old documents
                stmt = select(Document).where(
                    and_(
                        Document.created_at < cutoff_date,
                        Document.processing_status.in_(["completed", "failed"])
                    )
                )
                result = await db.execute(stmt)
                old_documents = result.scalars().all()
                
                deleted_count = 0
                failed_count = 0
                
                for doc in old_documents:
                    try:
                        success = await document_processor.delete_document(db, doc.id)
                        if success:
                            deleted_count += 1
                        else:
                            failed_count += 1
                    except Exception as e:
                        logger.error(f"Failed to delete document {doc.id}: {e}")
                        failed_count += 1
                
                return {
                    "success": True,
                    "deleted_count": deleted_count,
                    "failed_count": failed_count,
                    "cutoff_date": cutoff_date.isoformat()
                }
        
        result = asyncio.run(_cleanup())
        logger.info(f"Document cleanup completed: {result['deleted_count']} deleted, {result['failed_count']} failed")
        return result
        
    except Exception as e:
        logger.error(f"Error in document cleanup task: {e}")
        return {"success": False, "error": str(e)} 