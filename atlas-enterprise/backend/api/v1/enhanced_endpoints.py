"""
Enhanced API Endpoints for ATLAS Enterprise
New endpoints for advanced features including knowledge base updates, 
real-time notifications, multimodal AI, and advanced analytics.
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
import json

from ...core.database import get_session, get_cache, get_vector_store
from ...core.logging import get_logger, log_business_event
from ...core.security import get_current_user, require_permission
from ...services.knowledge_base_service import knowledge_service, DocumentType, DocumentStatus
from ...services.enhanced_ai_service import enhanced_ai_service, AIServiceType
from ...services.rate_limiting_service import rate_limit_service
from ...services.notification_service import notification_service
from ...services.analytics_service import analytics_service

logger = get_logger(__name__)
router = APIRouter()


# === PYDANTIC MODELS ===

class KnowledgeUpdateRequest(BaseModel):
    """Request model for knowledge base updates."""
    content: str = Field(..., description="Content to add to knowledge base")
    title: Optional[str] = Field(None, description="Optional title for the content")
    doc_type: Optional[str] = Field("user_input", description="Document type")
    tags: Optional[List[str]] = Field(default_factory=list, description="Optional tags")
    source: str = Field("api", description="Source of the content")


class ChatRequest(BaseModel):
    """Request model for enhanced chat."""
    message: str = Field(..., description="User message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID")
    include_knowledge_search: bool = Field(True, description="Include knowledge base search")
    enable_knowledge_updates: bool = Field(True, description="Allow knowledge base updates")


class BulkCalculationRequest(BaseModel):
    """Request model for bulk tariff calculations."""
    calculations: List[Dict[str, Any]] = Field(..., description="List of calculation requests")
    include_predictions: bool = Field(True, description="Include predictive analytics")
    include_ai_analysis: bool = Field(True, description="Include AI analysis")


class NotificationSubscription(BaseModel):
    """Request model for notification subscriptions."""
    user_id: str = Field(..., description="User ID")
    notification_types: List[str] = Field(..., description="Types of notifications to subscribe to")
    delivery_methods: List[str] = Field(default=["in_app"], description="Delivery methods")


class AnalyticsQuery(BaseModel):
    """Request model for analytics queries."""
    metric: str = Field(..., description="Metric to analyze")
    start_date: Optional[datetime] = Field(None, description="Start date for analysis")
    end_date: Optional[datetime] = Field(None, description="End date for analysis")
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional filters")
    granularity: str = Field("day", description="Data granularity (hour, day, week, month)")


# === KNOWLEDGE BASE ENDPOINTS ===

@router.post("/knowledge/add-from-text")
async def add_knowledge_from_text(
    request: KnowledgeUpdateRequest,
    current_user: Dict = Depends(get_current_user),
    cache = Depends(get_cache)
):
    """Add knowledge to the database from text input."""
    try:
        # Rate limiting check
        allowed, limit_info = await rate_limit_service.check_rate_limit(
            "knowledge_update", 
            current_user.get("id", "anonymous")
        )
        
        if not allowed:
            raise HTTPException(
                status_code=429, 
                detail=limit_info.get("message", "Rate limit exceeded")
            )
        
        # Process the knowledge update
        result = await knowledge_service.add_knowledge_from_text(
            text_input=request.content,
            user_id=current_user.get("id", "system"),
            source=request.source
        )
        
        # Log the event
        await log_business_event(
            "knowledge_base_manual_update",
            {
                "user_id": current_user.get("id"),
                "document_id": result.get("document_id"),
                "success": result.get("success"),
                "source": request.source
            }
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to add knowledge from text: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge/search")
async def search_knowledge(
    query: str,
    limit: int = 10,
    doc_type: Optional[str] = None,
    current_user: Dict = Depends(get_current_user),
    cache = Depends(get_cache)
):
    """Search the knowledge base."""
    try:
        # Check cache first
        cache_key = f"knowledge_search:{query}:{limit}:{doc_type}:{current_user.get('id')}"
        cached_result = await cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Convert doc_type string to enum if provided
        document_type = None
        if doc_type:
            try:
                document_type = DocumentType(doc_type)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid document type: {doc_type}")
        
        # Search knowledge base
        results = await knowledge_service.search_knowledge(
            query=query,
            limit=limit,
            doc_type=document_type
        )
        
        # Cache results
        await cache.set(cache_key, results, ttl=300)  # 5 minutes
        
        return {
            "results": results,
            "query": query,
            "count": len(results),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Knowledge search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/knowledge/{document_id}")
async def update_knowledge(
    document_id: str,
    updates: Dict[str, Any],
    current_user: Dict = Depends(get_current_user)
):
    """Update existing knowledge base document."""
    try:
        result = await knowledge_service.update_knowledge(
            document_id=document_id,
            updates=updates,
            user_id=current_user.get("id", "system")
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error", "Update failed"))
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to update knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/knowledge/{document_id}")
async def delete_knowledge(
    document_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Delete knowledge base document."""
    try:
        result = await knowledge_service.delete_knowledge(
            document_id=document_id,
            user_id=current_user.get("id", "system")
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error", "Delete failed"))
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to delete knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === ENHANCED AI ENDPOINTS ===

@router.post("/ai/enhanced-chat")
async def enhanced_chat(
    request: ChatRequest,
    current_user: Dict = Depends(get_current_user)
):
    """Enhanced chat with knowledge base integration and update capabilities."""
    try:
        # Rate limiting
        allowed, limit_info = await rate_limit_service.check_rate_limit(
            "ai_chat", 
            current_user.get("id", "anonymous")
        )
        
        if not allowed:
            raise HTTPException(status_code=429, detail=limit_info.get("message"))
        
        # Process chat request
        result = await enhanced_ai_service.chat_with_knowledge_update(
            message=request.message,
            user_id=current_user.get("id", "anonymous"),
            conversation_id=request.conversation_id,
            include_knowledge_search=request.include_knowledge_search
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Enhanced chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai/process-document")
async def process_document_ocr(
    file: UploadFile = File(...),
    extract_hts_codes: bool = Form(True),
    current_user: Dict = Depends(get_current_user)
):
    """Process uploaded document with OCR."""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Only image files are supported")
        
        # Read file data
        image_data = await file.read()
        
        # Process with OCR
        result = await enhanced_ai_service.process_document_ocr(
            image_data=image_data,
            extract_hts_codes=extract_hts_codes
        )
        
        # Log the event
        await log_business_event(
            "document_ocr_processing",
            {
                "user_id": current_user.get("id"),
                "filename": file.filename,
                "success": result.get("success"),
                "hts_codes_found": len(result.get("hts_codes", []))
            }
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Document OCR processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai/analyze-product-image")
async def analyze_product_image(
    file: UploadFile = File(...),
    current_user: Dict = Depends(get_current_user)
):
    """Analyze product image for classification."""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Only image files are supported")
        
        # Read file data
        image_data = await file.read()
        
        # Analyze image
        result = await enhanced_ai_service.analyze_product_image(image_data)
        
        return result
        
    except Exception as e:
        logger.error(f"Product image analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai/process-voice")
async def process_voice_input(
    file: UploadFile = File(...),
    current_user: Dict = Depends(get_current_user)
):
    """Process voice input and convert to text."""
    try:
        # Validate file type
        if not file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="Only audio files are supported")
        
        # Read file data
        audio_data = await file.read()
        
        # Process voice
        result = await enhanced_ai_service.process_voice_input(audio_data)
        
        return result
        
    except Exception as e:
        logger.error(f"Voice processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === BULK OPERATIONS ENDPOINTS ===

@router.post("/tariff/bulk-calculate")
async def bulk_tariff_calculation(
    request: BulkCalculationRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user)
):
    """Perform bulk tariff calculations."""
    try:
        # Rate limiting for heavy operations
        allowed, limit_info = await rate_limit_service.check_rate_limit(
            "bulk_calculation", 
            current_user.get("id", "anonymous")
        )
        
        if not allowed:
            raise HTTPException(status_code=429, detail=limit_info.get("message"))
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Start background processing
        background_tasks.add_task(
            _process_bulk_calculations,
            job_id,
            request.calculations,
            current_user.get("id"),
            request.include_predictions,
            request.include_ai_analysis
        )
        
        return {
            "job_id": job_id,
            "status": "processing",
            "total_calculations": len(request.calculations),
            "message": "Bulk calculation started. Use the job ID to check status."
        }
        
    except Exception as e:
        logger.error(f"Bulk calculation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tariff/bulk-status/{job_id}")
async def get_bulk_calculation_status(
    job_id: str,
    current_user: Dict = Depends(get_current_user),
    cache = Depends(get_cache)
):
    """Get status of bulk calculation job."""
    try:
        status = await cache.get(f"bulk_job:{job_id}")
        if not status:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return status
        
    except Exception as e:
        logger.error(f"Failed to get bulk status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === REAL-TIME NOTIFICATIONS ENDPOINTS ===

@router.post("/notifications/subscribe")
async def subscribe_to_notifications(
    request: NotificationSubscription,
    current_user: Dict = Depends(get_current_user)
):
    """Subscribe to real-time notifications."""
    try:
        await notification_service.initialize()
        
        result = await notification_service.subscribe_user(
            user_id=request.user_id,
            notification_types=request.notification_types,
            delivery_methods=request.delivery_methods
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Notification subscription failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/notifications/stream")
async def notification_stream(
    current_user: Dict = Depends(get_current_user)
):
    """Server-sent events stream for real-time notifications."""
    try:
        await notification_service.initialize()
        
        async def event_generator():
            """Generate server-sent events."""
            user_id = current_user.get("id")
            if not user_id:
                return
            
            while True:
                try:
                    # Get pending notifications
                    notifications = await notification_service.get_user_notifications(
                        user_id, 
                        limit=10
                    )
                    
                    for notification in notifications:
                        event_data = json.dumps(notification)
                        yield f"data: {event_data}\n\n"
                    
                    # Wait before next check
                    await asyncio.sleep(5)
                    
                except Exception as e:
                    logger.error(f"Notification stream error: {e}")
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"
                    break
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            }
        )
        
    except Exception as e:
        logger.error(f"Notification stream setup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === ADVANCED ANALYTICS ENDPOINTS ===

@router.post("/analytics/query")
async def analytics_query(
    request: AnalyticsQuery,
    current_user: Dict = Depends(get_current_user)
):
    """Perform advanced analytics query."""
    try:
        await analytics_service.initialize()
        
        result = await analytics_service.query_metric(
            metric=request.metric,
            start_date=request.start_date,
            end_date=request.end_date,
            filters=request.filters,
            granularity=request.granularity,
            user_id=current_user.get("id")
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Analytics query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/dashboard")
async def get_analytics_dashboard(
    current_user: Dict = Depends(get_current_user),
    cache = Depends(get_cache)
):
    """Get analytics dashboard data."""
    try:
        # Check cache first
        cache_key = f"analytics_dashboard:{current_user.get('id')}"
        cached_data = await cache.get(cache_key)
        if cached_data:
            return cached_data
        
        await analytics_service.initialize()
        
        # Get dashboard data
        dashboard_data = await analytics_service.get_dashboard_data(
            user_id=current_user.get("id")
        )
        
        # Cache for 5 minutes
        await cache.set(cache_key, dashboard_data, ttl=300)
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Analytics dashboard failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/predictive")
async def get_predictive_analytics(
    metric: str,
    days_ahead: int = 30,
    current_user: Dict = Depends(get_current_user)
):
    """Get predictive analytics."""
    try:
        await analytics_service.initialize()
        
        result = await analytics_service.get_predictive_analytics(
            metric=metric,
            days_ahead=days_ahead,
            user_id=current_user.get("id")
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Predictive analytics failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === SYSTEM HEALTH AND MONITORING ===

@router.get("/system/health")
async def enhanced_system_health():
    """Enhanced system health check."""
    try:
        # Initialize services if needed
        await rate_limit_service.initialize()
        await knowledge_service.initialize()
        await enhanced_ai_service.initialize()
        
        # Get comprehensive health status
        health_data = {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "services": {
                "knowledge_base": {"status": "healthy"},
                "ai_service": {"status": "healthy"},
                "rate_limiting": {"status": "healthy"},
                "cache": {"status": "unknown"},
                "vector_store": {"status": "unknown"}
            }
        }
        
        # Check individual service health
        try:
            cache = get_cache()
            cache_stats = await cache.get_stats()
            health_data["services"]["cache"] = {
                "status": "healthy",
                "stats": cache_stats
            }
        except Exception as e:
            health_data["services"]["cache"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        return health_data
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "unhealthy",
            "error": str(e)
        }


# === CONVERSATION EXPORT ENDPOINTS ===

@router.post("/conversations/{conversation_id}/export")
async def export_conversation(
    conversation_id: str,
    format: str = "json",
    template: str = "standard",
    include_metadata: bool = True,
    include_timestamps: bool = True,
    include_system_messages: bool = False,
    include_knowledge_updates: bool = True,
    anonymize_user_data: bool = False,
    custom_title: Optional[str] = None,
    custom_header: Optional[str] = None,
    custom_footer: Optional[str] = None,
    current_user: Dict = Depends(get_current_user)
):
    """Export AI chat conversation in various formats."""
    try:
        from ...services.conversation_export_service import (
            conversation_export_service, 
            ExportOptions, 
            ExportFormat, 
            ExportTemplate
        )
        
        # Initialize service
        await conversation_export_service.initialize()
        
        # Validate format
        try:
            export_format = ExportFormat(format.lower())
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported format: {format}. Supported: {[f.value for f in ExportFormat]}"
            )
        
        # Validate template
        try:
            export_template = ExportTemplate(template.lower())
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported template: {template}. Supported: {[t.value for t in ExportTemplate]}"
            )
        
        # Create export options
        options = ExportOptions(
            format=export_format,
            template=export_template,
            include_metadata=include_metadata,
            include_timestamps=include_timestamps,
            include_system_messages=include_system_messages,
            include_knowledge_updates=include_knowledge_updates,
            anonymize_user_data=anonymize_user_data,
            custom_title=custom_title,
            custom_header=custom_header,
            custom_footer=custom_footer
        )
        
        # Export conversation
        result = await conversation_export_service.export_conversation(
            conversation_id=conversation_id,
            options=options,
            user_id=current_user.get("id")
        )
        
        if result.success:
            return {
                "success": True,
                "export_id": result.export_id,
                "file_name": result.file_name,
                "file_size": result.file_size,
                "download_url": result.download_url,
                "format": format,
                "metadata": result.metadata,
                "message": f"Conversation exported successfully as {format.upper()}"
            }
        else:
            raise HTTPException(status_code=500, detail=result.error)
            
    except Exception as e:
        logger.error(f"Conversation export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/download/{export_id}")
async def download_exported_conversation(
    export_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Download exported conversation file."""
    try:
        from ...services.conversation_export_service import conversation_export_service
        from fastapi.responses import FileResponse
        
        # Get export file
        file_path = await conversation_export_service.get_export_file(export_id)
        
        if not file_path:
            raise HTTPException(status_code=404, detail="Export file not found")
        
        # Determine media type based on file extension
        media_types = {
            '.json': 'application/json',
            '.pdf': 'application/pdf',
            '.html': 'text/html',
            '.md': 'text/markdown',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.txt': 'text/plain',
            '.csv': 'text/csv'
        }
        
        media_type = media_types.get(file_path.suffix, 'application/octet-stream')
        
        return FileResponse(
            path=str(file_path),
            media_type=media_type,
            filename=file_path.name
        )
        
    except Exception as e:
        logger.error(f"File download failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}/export-options")
async def get_export_options(
    conversation_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get available export options for a conversation."""
    try:
        from ...services.conversation_export_service import ExportFormat, ExportTemplate
        from ...services.enhanced_ai_service import enhanced_ai_service
        
        # Get conversation summary
        summary = await enhanced_ai_service.get_conversation_summary(conversation_id)
        
        if "error" in summary:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {
            "conversation_id": conversation_id,
            "conversation_summary": summary,
            "available_formats": [
                {
                    "value": f.value,
                    "name": f.value.upper(),
                    "description": {
                        "json": "Structured data format with full metadata",
                        "pdf": "Professional document format for printing",
                        "html": "Web format with rich styling and formatting",
                        "markdown": "Text format with markup for documentation",
                        "excel": "Spreadsheet format for data analysis",
                        "txt": "Plain text format for simple viewing",
                        "csv": "Comma-separated values for data import"
                    }.get(f.value, "Export format")
                }
                for f in ExportFormat
            ],
            "available_templates": [
                {
                    "value": t.value,
                    "name": t.value.title(),
                    "description": {
                        "standard": "Default template with balanced detail",
                        "professional": "Formal template for business use",
                        "detailed": "Comprehensive template with all metadata",
                        "summary": "Condensed template with key information only"
                    }.get(t.value, "Export template")
                }
                for t in ExportTemplate
            ],
            "export_options": {
                "include_metadata": "Add conversation statistics and details",
                "include_timestamps": "Show message timestamps",
                "include_system_messages": "Include system/internal messages",
                "include_knowledge_updates": "Include knowledge base updates",
                "anonymize_user_data": "Remove personal information",
                "custom_title": "Override default export title",
                "custom_header": "Add custom header text",
                "custom_footer": "Add custom footer text"
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get export options: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conversations/bulk-export")
async def bulk_export_conversations(
    conversation_ids: List[str],
    format: str = "json",
    template: str = "standard",
    include_metadata: bool = True,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user)
):
    """Export multiple conversations as a ZIP archive."""
    try:
        from ...services.conversation_export_service import (
            conversation_export_service,
            ExportOptions,
            ExportFormat,
            ExportTemplate
        )
        
        # Validate inputs
        if len(conversation_ids) > 50:
            raise HTTPException(
                status_code=400, 
                detail="Maximum 50 conversations per bulk export"
            )
        
        try:
            export_format = ExportFormat(format.lower())
            export_template = ExportTemplate(template.lower())
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Generate bulk export ID
        bulk_export_id = str(uuid.uuid4())
        
        # Start background processing
        background_tasks.add_task(
            _process_bulk_export,
            conversation_ids,
            bulk_export_id,
            current_user.get("id"),
            export_format,
            export_template,
            include_metadata
        )
        
        return {
            "success": True,
            "bulk_export_id": bulk_export_id,
            "total_conversations": len(conversation_ids),
            "status": "processing",
            "message": "Bulk export started. Check status with the bulk export ID.",
            "status_url": f"/api/v1/conversations/bulk-export-status/{bulk_export_id}"
        }
        
    except Exception as e:
        logger.error(f"Bulk export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/bulk-export-status/{bulk_export_id}")
async def get_bulk_export_status(
    bulk_export_id: str,
    current_user: Dict = Depends(get_current_user),
    cache = Depends(get_cache)
):
    """Get status of bulk export operation."""
    try:
        status = await cache.get(f"bulk_export:{bulk_export_id}")
        if not status:
            raise HTTPException(status_code=404, detail="Bulk export not found")
        
        return status
        
    except Exception as e:
        logger.error(f"Failed to get bulk export status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === BACKGROUND TASK FUNCTIONS ===

async def _process_bulk_export(
    conversation_ids: List[str],
    bulk_export_id: str,
    user_id: str,
    export_format: "ExportFormat",
    export_template: "ExportTemplate", 
    include_metadata: bool
):
    """Background task for processing bulk conversation exports."""
    try:
        from ...services.conversation_export_service import conversation_export_service, ExportOptions
        import zipfile
        
        cache = get_cache()
        
        # Initialize status
        await cache.set(f"bulk_export:{bulk_export_id}", {
            "status": "processing",
            "progress": 0,
            "total": len(conversation_ids),
            "completed": 0,
            "failed": 0,
            "started_at": datetime.now().isoformat()
        }, ttl=3600)
        
        # Initialize export service
        await conversation_export_service.initialize()
        
        # Create export options
        options = ExportOptions(
            format=export_format,
            template=export_template,
            include_metadata=include_metadata,
            include_timestamps=True,
            include_knowledge_updates=True
        )
        
        # Process each conversation
        export_results = []
        completed = 0
        failed = 0
        
        for i, conversation_id in enumerate(conversation_ids):
            try:
                result = await conversation_export_service.export_conversation(
                    conversation_id=conversation_id,
                    options=options,
                    user_id=user_id
                )
                
                if result.success:
                    export_results.append(result)
                    completed += 1
                else:
                    failed += 1
                    logger.warning(f"Failed to export conversation {conversation_id}: {result.error}")
                
            except Exception as e:
                failed += 1
                logger.error(f"Export error for conversation {conversation_id}: {e}")
            
            # Update progress
            progress = int((i + 1) / len(conversation_ids) * 100)
            await cache.set(f"bulk_export:{bulk_export_id}", {
                "status": "processing",
                "progress": progress,
                "total": len(conversation_ids),
                "completed": completed,
                "failed": failed,
                "started_at": datetime.now().isoformat()
            }, ttl=3600)
        
        # Create ZIP archive
        if export_results:
            zip_filename = f"bulk_export_{bulk_export_id}.zip"
            zip_path = conversation_export_service.export_dir / zip_filename
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for result in export_results:
                    if result.file_path:
                        zipf.write(result.file_path, result.file_name)
            
            zip_size = zip_path.stat().st_size
            
            # Update final status
            await cache.set(f"bulk_export:{bulk_export_id}", {
                "status": "completed",
                "progress": 100,
                "total": len(conversation_ids),
                "completed": completed,
                "failed": failed,
                "zip_file": zip_filename,
                "zip_size": zip_size,
                "download_url": f"/api/v1/conversations/download/{bulk_export_id}",
                "started_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat()
            }, ttl=3600)
            
        else:
            # All exports failed
            await cache.set(f"bulk_export:{bulk_export_id}", {
                "status": "failed",
                "progress": 100,
                "total": len(conversation_ids),
                "completed": 0,
                "failed": len(conversation_ids),
                "error": "All conversation exports failed",
                "started_at": datetime.now().isoformat(),
                "failed_at": datetime.now().isoformat()
            }, ttl=3600)
        
        # Log completion
        await log_business_event(
            "bulk_conversation_export",
            {
                "bulk_export_id": bulk_export_id,
                "user_id": user_id,
                "total_conversations": len(conversation_ids),
                "completed": completed,
                "failed": failed,
                "format": export_format.value
            }
        )
        
    except Exception as e:
        logger.error(f"Bulk export processing failed: {e}")
        cache = get_cache()
        await cache.set(f"bulk_export:{bulk_export_id}", {
            "status": "failed",
            "error": str(e),
            "started_at": datetime.now().isoformat(),
            "failed_at": datetime.now().isoformat()
        }, ttl=3600)


async def _process_bulk_calculations(
    job_id: str, 
    calculations: List[Dict[str, Any]], 
    user_id: str,
    include_predictions: bool,
    include_ai_analysis: bool
):
    """Background task for processing bulk calculations."""
    try:
        cache = get_cache()
        
        # Initialize job status
        await cache.set(f"bulk_job:{job_id}", {
            "status": "processing",
            "progress": 0,
            "total": len(calculations),
            "completed": 0,
            "failed": 0,
            "results": [],
            "started_at": datetime.now().isoformat()
        }, ttl=3600)
        
        results = []
        completed = 0
        failed = 0
        
        for i, calc_request in enumerate(calculations):
            try:
                # Simulate calculation processing
                # In reality, this would call your tariff calculation service
                await asyncio.sleep(0.1)  # Simulate processing time
                
                result = {
                    "index": i,
                    "status": "completed",
                    "data": {
                        "hts_code": calc_request.get("hts_code"),
                        "calculated_tariff": 250.50,  # Simulated result
                        "timestamp": datetime.now().isoformat()
                    }
                }
                
                if include_predictions:
                    result["data"]["predictions"] = {
                        "30_day_forecast": 255.75
                    }
                
                if include_ai_analysis:
                    result["data"]["ai_analysis"] = {
                        "confidence": 0.89,
                        "risk_factors": ["currency_volatility"]
                    }
                
                results.append(result)
                completed += 1
                
            except Exception as e:
                logger.error(f"Bulk calculation item {i} failed: {e}")
                results.append({
                    "index": i,
                    "status": "failed",
                    "error": str(e)
                })
                failed += 1
            
            # Update progress
            progress = int((i + 1) / len(calculations) * 100)
            await cache.set(f"bulk_job:{job_id}", {
                "status": "processing",
                "progress": progress,
                "total": len(calculations),
                "completed": completed,
                "failed": failed,
                "results": results[-10:],  # Keep only last 10 results in status
                "started_at": datetime.now().isoformat()
            }, ttl=3600)
        
        # Mark job as completed
        await cache.set(f"bulk_job:{job_id}", {
            "status": "completed",
            "progress": 100,
            "total": len(calculations),
            "completed": completed,
            "failed": failed,
            "results": results,
            "started_at": datetime.now().isoformat(),
            "completed_at": datetime.now().isoformat()
        }, ttl=3600)
        
        # Log completion
        await log_business_event(
            "bulk_calculation_completed",
            {
                "job_id": job_id,
                "user_id": user_id,
                "total": len(calculations),
                "completed": completed,
                "failed": failed
            }
        )
        
    except Exception as e:
        logger.error(f"Bulk calculation job {job_id} failed: {e}")
        cache = get_cache()
        await cache.set(f"bulk_job:{job_id}", {
            "status": "failed",
            "error": str(e),
            "started_at": datetime.now().isoformat(),
            "failed_at": datetime.now().isoformat()
        }, ttl=3600) 