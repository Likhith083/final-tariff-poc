from prometheus_client import Counter, Histogram, Gauge, Summary, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
from fastapi.responses import StreamingResponse
import time
import psutil
import asyncio
from typing import Dict, Any
from loguru import logger
import json

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'http_active_connections',
    'Number of active HTTP connections'
)

DATABASE_CONNECTIONS = Gauge(
    'database_connections',
    'Number of active database connections'
)

REDIS_CONNECTIONS = Gauge(
    'redis_connections',
    'Number of active Redis connections'
)

AI_REQUESTS = Counter(
    'ai_requests_total',
    'Total AI/LLM requests',
    ['model', 'endpoint']
)

AI_RESPONSE_TIME = Histogram(
    'ai_response_time_seconds',
    'AI response time in seconds',
    ['model', 'endpoint']
)

TARIFF_CALCULATIONS = Counter(
    'tariff_calculations_total',
    'Total tariff calculations',
    ['hts_code', 'country']
)

ERROR_COUNT = Counter(
    'errors_total',
    'Total errors',
    ['type', 'endpoint']
)

class MonitoringMiddleware:
    """Middleware for collecting metrics and monitoring"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = time.time()
            
            # Track active connections
            ACTIVE_CONNECTIONS.inc()
            
            async def send_with_metrics(message):
                if message["type"] == "http.response.start":
                    # Record request metrics
                    method = scope.get("method", "UNKNOWN")
                    path = scope.get("path", "/")
                    status = message.get("status", 500)
                    
                    REQUEST_COUNT.labels(
                        method=method,
                        endpoint=path,
                        status=status
                    ).inc()
                    
                    # Record duration
                    duration = time.time() - start_time
                    REQUEST_DURATION.labels(
                        method=method,
                        endpoint=path
                    ).observe(duration)
                    
                    # Track errors
                    if status >= 400:
                        ERROR_COUNT.labels(
                            type="http_error",
                            endpoint=path
                        ).inc()
                
                elif message["type"] == "http.response.end":
                    # Decrease active connections
                    ACTIVE_CONNECTIONS.dec()
                
                await send(message)
            
            await self.app(scope, receive, send_with_metrics)
        else:
            await self.app(scope, receive, send)

class HealthChecker:
    """Health check service for monitoring system health"""
    
    def __init__(self, redis_client=None, database_session=None):
        self.redis_client = redis_client
        self.database_session = database_session
    
    async def check_system_health(self) -> Dict[str, Any]:
        """Check overall system health"""
        health_status = {
            "status": "healthy",
            "timestamp": time.time(),
            "checks": {}
        }
        
        # Check system resources
        health_status["checks"]["system"] = await self._check_system_resources()
        
        # Check database
        if self.database_session:
            health_status["checks"]["database"] = await self._check_database()
        
        # Check Redis
        if self.redis_client:
            health_status["checks"]["redis"] = await self._check_redis()
        
        # Check external services
        health_status["checks"]["external_services"] = await self._check_external_services()
        
        # Determine overall status
        all_healthy = all(
            check.get("status") == "healthy" 
            for check in health_status["checks"].values()
        )
        
        health_status["status"] = "healthy" if all_healthy else "unhealthy"
        
        return health_status
    
    async def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            status = "healthy"
            if cpu_percent > 80 or memory.percent > 85 or disk.percent > 90:
                status = "warning"
            
            return {
                "status": status,
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "memory_available": memory.available,
                "disk_free": disk.free
            }
        except Exception as e:
            logger.error(f"System resource check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    async def _check_database(self) -> Dict[str, Any]:
        """Check database connectivity"""
        try:
            # Simple query to test connection
            result = await self.database_session.execute("SELECT 1")
            return {"status": "healthy", "response_time": 0.001}
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    async def _check_redis(self) -> Dict[str, Any]:
        """Check Redis connectivity"""
        try:
            start_time = time.time()
            await self.redis_client.ping()
            response_time = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time": response_time
            }
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    async def _check_external_services(self) -> Dict[str, Any]:
        """Check external service dependencies"""
        services = {}
        
        # Check Ollama service
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                start_time = time.time()
                response = await client.get("http://ollama:11434/api/tags", timeout=5)
                response_time = time.time() - start_time
                
                services["ollama"] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time": response_time,
                    "status_code": response.status_code
                }
        except Exception as e:
            services["ollama"] = {"status": "unhealthy", "error": str(e)}
        
        return services

class PerformanceMonitor:
    """Performance monitoring and profiling"""
    
    def __init__(self):
        self.metrics = {}
    
    async def track_ai_request(self, model: str, endpoint: str, func):
        """Track AI request performance"""
        start_time = time.time()
        
        try:
            result = await func()
            duration = time.time() - start_time
            
            AI_REQUESTS.labels(model=model, endpoint=endpoint).inc()
            AI_RESPONSE_TIME.labels(model=model, endpoint=endpoint).observe(duration)
            
            return result
        except Exception as e:
            duration = time.time() - start_time
            ERROR_COUNT.labels(type="ai_error", endpoint=endpoint).inc()
            logger.error(f"AI request failed: {e}")
            raise
    
    def track_tariff_calculation(self, hts_code: str, country: str):
        """Track tariff calculation metrics"""
        TARIFF_CALCULATIONS.labels(hts_code=hts_code, country=country).inc()
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return {
            "active_connections": ACTIVE_CONNECTIONS._value.get(),
            "total_requests": REQUEST_COUNT._value.get(),
            "error_rate": ERROR_COUNT._value.get(),
            "system_resources": {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent
            }
        }

# Metrics endpoint
async def metrics_endpoint():
    """Prometheus metrics endpoint"""
    return StreamingResponse(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

# Health check endpoint
async def health_check_endpoint(health_checker: HealthChecker):
    """Health check endpoint"""
    health_status = await health_checker.check_system_health()
    
    status_code = 200 if health_status["status"] == "healthy" else 503
    
    return Response(
        content=json.dumps(health_status, indent=2),
        media_type="application/json",
        status_code=status_code
    ) 