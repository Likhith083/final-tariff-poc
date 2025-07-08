"""
Rate Limiting Service for ATLAS Enterprise
Advanced rate limiting with Redis-based storage and intelligent throttling.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

from ..core.database import get_cache
from ..core.logging import get_logger
from ..core.config import settings

logger = get_logger(__name__)


class RateLimitType(Enum):
    """Rate limit types."""
    PER_IP = "per_ip"
    PER_USER = "per_user"
    PER_API_KEY = "per_api_key"
    GLOBAL = "global"


class RateLimitWindow(Enum):
    """Rate limit time windows."""
    SECOND = "second"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"


@dataclass
class RateLimit:
    """Rate limit configuration."""
    max_requests: int
    window: RateLimitWindow
    limit_type: RateLimitType
    burst_allowance: int = 0  # Additional requests allowed in burst
    cooldown_period: int = 300  # Cooldown after limit exceeded (seconds)


class RateLimitService:
    """Advanced rate limiting service."""
    
    def __init__(self):
        """Initialize rate limiting service."""
        self.cache = None
        self.default_limits = {
            # Standard API limits
            "api_standard": RateLimit(100, RateLimitWindow.MINUTE, RateLimitType.PER_IP),
            "api_burst": RateLimit(10, RateLimitWindow.SECOND, RateLimitType.PER_IP, burst_allowance=5),
            
            # AI-specific limits (more restrictive due to cost)
            "ai_classification": RateLimit(50, RateLimitWindow.HOUR, RateLimitType.PER_USER),
            "ai_chat": RateLimit(20, RateLimitWindow.MINUTE, RateLimitType.PER_USER),
            
            # Knowledge base updates (prevent spam)
            "knowledge_update": RateLimit(10, RateLimitWindow.HOUR, RateLimitType.PER_USER),
            
            # Heavy operations
            "bulk_calculation": RateLimit(5, RateLimitWindow.MINUTE, RateLimitType.PER_USER),
            "web_scraping": RateLimit(1, RateLimitWindow.MINUTE, RateLimitType.GLOBAL),
            
            # Authentication
            "auth_login": RateLimit(5, RateLimitWindow.MINUTE, RateLimitType.PER_IP),
            "auth_register": RateLimit(3, RateLimitWindow.HOUR, RateLimitType.PER_IP),
        }
        self._initialized = False
    
    async def initialize(self):
        """Initialize the rate limiting service."""
        if self._initialized:
            return
        
        self.cache = get_cache()
        self._initialized = True
        logger.info("Rate limiting service initialized")
    
    def _get_window_seconds(self, window: RateLimitWindow) -> int:
        """Get window size in seconds."""
        window_mapping = {
            RateLimitWindow.SECOND: 1,
            RateLimitWindow.MINUTE: 60,
            RateLimitWindow.HOUR: 3600,
            RateLimitWindow.DAY: 86400
        }
        return window_mapping[window]
    
    def _get_rate_limit_key(self, limit_type: RateLimitType, identifier: str, 
                           endpoint: str, window: RateLimitWindow) -> str:
        """Generate rate limit key for Redis."""
        current_window = int(time.time() // self._get_window_seconds(window))
        return f"rate_limit:{limit_type.value}:{identifier}:{endpoint}:{current_window}"
    
    async def check_rate_limit(self, endpoint: str, identifier: str, 
                             limit_type: RateLimitType = RateLimitType.PER_IP,
                             custom_limit: Optional[RateLimit] = None) -> Tuple[bool, Dict[str, Any]]:
        """Check if request is within rate limit."""
        try:
            # Get rate limit configuration
            rate_limit = custom_limit or self.default_limits.get(endpoint)
            if not rate_limit:
                # No rate limit configured, allow request
                return True, {"allowed": True, "reason": "no_limit_configured"}
            
            # Check if user is in cooldown
            cooldown_key = f"rate_limit_cooldown:{limit_type.value}:{identifier}:{endpoint}"
            in_cooldown = await self.cache.get(cooldown_key)
            if in_cooldown:
                return False, {
                    "allowed": False,
                    "reason": "cooldown_active",
                    "retry_after": rate_limit.cooldown_period,
                    "message": f"Rate limit exceeded. Try again in {rate_limit.cooldown_period} seconds."
                }
            
            # Get current request count
            rate_key = self._get_rate_limit_key(
                limit_type, identifier, endpoint, rate_limit.window
            )
            
            current_count = await self.cache.get(rate_key) or 0
            window_seconds = self._get_window_seconds(rate_limit.window)
            
            # Calculate effective limit (including burst allowance)
            effective_limit = rate_limit.max_requests + rate_limit.burst_allowance
            
            if current_count >= effective_limit:
                # Set cooldown period
                await self.cache.set(cooldown_key, True, rate_limit.cooldown_period)
                
                return False, {
                    "allowed": False,
                    "reason": "rate_limit_exceeded",
                    "limit": rate_limit.max_requests,
                    "window": rate_limit.window.value,
                    "current_count": current_count,
                    "retry_after": window_seconds,
                    "message": f"Rate limit exceeded: {current_count}/{rate_limit.max_requests} requests per {rate_limit.window.value}"
                }
            
            # Increment counter
            new_count = current_count + 1
            await self.cache.set(rate_key, new_count, window_seconds)
            
            return True, {
                "allowed": True,
                "limit": rate_limit.max_requests,
                "window": rate_limit.window.value,
                "current_count": new_count,
                "remaining": max(0, rate_limit.max_requests - new_count),
                "reset_time": int(time.time()) + window_seconds
            }
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            # Allow request on error to avoid blocking service
            return True, {"allowed": True, "reason": "check_failed", "error": str(e)}
    
    async def get_rate_limit_status(self, endpoint: str, identifier: str,
                                  limit_type: RateLimitType = RateLimitType.PER_IP) -> Dict[str, Any]:
        """Get current rate limit status for an identifier."""
        try:
            rate_limit = self.default_limits.get(endpoint)
            if not rate_limit:
                return {"status": "no_limit", "endpoint": endpoint}
            
            rate_key = self._get_rate_limit_key(
                limit_type, identifier, endpoint, rate_limit.window
            )
            
            current_count = await self.cache.get(rate_key) or 0
            window_seconds = self._get_window_seconds(rate_limit.window)
            
            # Check cooldown status
            cooldown_key = f"rate_limit_cooldown:{limit_type.value}:{identifier}:{endpoint}"
            in_cooldown = await self.cache.get(cooldown_key)
            
            return {
                "endpoint": endpoint,
                "limit": rate_limit.max_requests,
                "window": rate_limit.window.value,
                "current_count": current_count,
                "remaining": max(0, rate_limit.max_requests - current_count),
                "reset_time": int(time.time()) + window_seconds,
                "in_cooldown": bool(in_cooldown),
                "burst_allowance": rate_limit.burst_allowance
            }
            
        except Exception as e:
            logger.error(f"Failed to get rate limit status: {e}")
            return {"error": str(e)}
    
    async def reset_rate_limit(self, endpoint: str, identifier: str,
                             limit_type: RateLimitType = RateLimitType.PER_IP) -> bool:
        """Reset rate limit for specific identifier (admin function)."""
        try:
            rate_limit = self.default_limits.get(endpoint)
            if not rate_limit:
                return True
            
            # Reset current window
            rate_key = self._get_rate_limit_key(
                limit_type, identifier, endpoint, rate_limit.window
            )
            await self.cache.delete(rate_key)
            
            # Reset cooldown
            cooldown_key = f"rate_limit_cooldown:{limit_type.value}:{identifier}:{endpoint}"
            await self.cache.delete(cooldown_key)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to reset rate limit: {e}")
            return False
    
    async def get_global_stats(self) -> Dict[str, Any]:
        """Get global rate limiting statistics."""
        try:
            # This would require scanning Redis keys, which should be done carefully
            # For now, return basic stats
            cache_stats = await self.cache.get_stats()
            
            return {
                "service_status": "active",
                "configured_endpoints": list(self.default_limits.keys()),
                "cache_stats": cache_stats,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get global stats: {e}")
            return {"error": str(e)}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for automatic rate limiting."""
    
    def __init__(self, app, rate_limit_service: RateLimitService):
        """Initialize rate limit middleware."""
        super().__init__(app)
        self.rate_limit_service = rate_limit_service
        
        # Endpoint mapping for rate limits
        self.endpoint_mapping = {
            "/api/v1/ai/chat": "ai_chat",
            "/api/v1/ai/classify": "ai_classification",
            "/api/v1/knowledge/add": "knowledge_update",
            "/api/v1/tariff/bulk-calculate": "bulk_calculation",
            "/api/v1/scraper/manual-scrape": "web_scraping",
            "/api/v1/auth/login": "auth_login",
            "/api/v1/auth/register": "auth_register"
        }
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        # Skip rate limiting for health checks and static files
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Get client identifier
        client_ip = request.client.host
        user_id = getattr(request.state, "user_id", None)
        api_key = request.headers.get("X-API-Key")
        
        # Determine identifier and limit type
        if api_key:
            identifier = api_key
            limit_type = RateLimitType.PER_API_KEY
        elif user_id:
            identifier = user_id
            limit_type = RateLimitType.PER_USER
        else:
            identifier = client_ip
            limit_type = RateLimitType.PER_IP
        
        # Find matching endpoint
        endpoint_key = "api_standard"  # Default
        for path_pattern, endpoint_name in self.endpoint_mapping.items():
            if request.url.path.startswith(path_pattern):
                endpoint_key = endpoint_name
                break
        
        # Check rate limit
        allowed, limit_info = await self.rate_limit_service.check_rate_limit(
            endpoint_key, identifier, limit_type
        )
        
        if not allowed:
            # Add rate limit headers
            headers = {
                "X-RateLimit-Limit": str(limit_info.get("limit", 0)),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(limit_info.get("retry_after", 60)),
                "Retry-After": str(limit_info.get("retry_after", 60))
            }
            
            raise HTTPException(
                status_code=429,
                detail=limit_info.get("message", "Rate limit exceeded"),
                headers=headers
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        if limit_info.get("allowed"):
            response.headers["X-RateLimit-Limit"] = str(limit_info.get("limit", 0))
            response.headers["X-RateLimit-Remaining"] = str(limit_info.get("remaining", 0))
            response.headers["X-RateLimit-Reset"] = str(limit_info.get("reset_time", 0))
        
        return response


# Global rate limit service
rate_limit_service = RateLimitService() 