"""
ATLAS Enterprise Logging Configuration
Structured logging with JSON output for enterprise monitoring.
"""

import logging
import sys
from typing import Any, Dict
import structlog
from pythonjsonlogger import jsonlogger

from .config import settings


def setup_logging() -> None:
    """Configure structured logging for the application."""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if settings.log_format == "json" else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    if settings.log_format == "json":
        formatter = jsonlogger.JsonFormatter(
            fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    # Setup handlers
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))
    root_logger.addHandler(handler)
    
    # Silence noisy loggers in development
    if settings.is_development:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
        logging.getLogger("asyncio").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return structlog.get_logger(name)


class LoggingMiddleware:
    """Middleware for logging HTTP requests and responses."""
    
    def __init__(self, app):
        self.app = app
        self.logger = get_logger(__name__)
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request_id = id(scope)  # Simple request ID
        method = scope["method"]
        path = scope["path"]
        
        # Log request
        self.logger.info(
            "HTTP request started",
            request_id=request_id,
            method=method,
            path=path,
            client=scope.get("client"),
        )
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status_code = message["status"]
                self.logger.info(
                    "HTTP request completed",
                    request_id=request_id,
                    method=method,
                    path=path,
                    status_code=status_code,
                )
            await send(message)
        
        await self.app(scope, receive, send_wrapper)


def log_business_event(
    event_type: str,
    user_id: str = None,
    details: Dict[str, Any] = None,
    **kwargs
) -> None:
    """
    Log business events for audit and analytics.
    
    Args:
        event_type: Type of business event
        user_id: User ID if applicable
        details: Additional event details
        **kwargs: Additional context
    """
    logger = get_logger("business_events")
    
    event_data = {
        "event_type": event_type,
        "user_id": user_id,
        "details": details or {},
        **kwargs
    }
    
    logger.info("Business event", **event_data) 