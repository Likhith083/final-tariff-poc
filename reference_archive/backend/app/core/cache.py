import redis.asyncio as redis
import json
import pickle
from typing import Any, Optional, Union, Dict, List
from datetime import timedelta
import hashlib
from loguru import logger
import asyncio

class CacheManager:
    """Enterprise cache manager with Redis backend"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.default_ttl = 3600  # 1 hour default
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        try:
            value = await self.redis.get(key)
            if value is None:
                return default
            
            # Try to deserialize as JSON first, then pickle
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return pickle.loads(value)
                
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return default
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            ttl = ttl or self.default_ttl
            
            # Try JSON serialization first, fallback to pickle
            try:
                serialized_value = json.dumps(value)
            except (TypeError, ValueError):
                serialized_value = pickle.dumps(value)
            
            await self.redis.setex(key, ttl, serialized_value)
            return True
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            result = await self.redis.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration for key"""
        try:
            return await self.redis.expire(key, ttl)
        except Exception as e:
            logger.error(f"Cache expire error for key {key}: {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment counter in cache"""
        try:
            return await self.redis.incrby(key, amount)
        except Exception as e:
            logger.error(f"Cache increment error for key {key}: {e}")
            return None
    
    async def get_or_set(self, key: str, default_func, ttl: Optional[int] = None) -> Any:
        """Get value from cache or set default if not exists"""
        value = await self.get(key)
        if value is not None:
            return value
        
        # Execute default function
        if asyncio.iscoroutinefunction(default_func):
            value = await default_func()
        else:
            value = default_func()
        
        # Cache the result
        await self.set(key, value, ttl)
        return value
    
    def generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_parts = [str(arg) for arg in args]
        key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()

class CacheDecorator:
    """Decorator for caching function results"""
    
    def __init__(self, cache_manager: CacheManager, ttl: Optional[int] = None, key_prefix: str = ""):
        self.cache_manager = cache_manager
        self.ttl = ttl
        self.key_prefix = key_prefix
    
    def __call__(self, func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{self.key_prefix}:{self.cache_manager.generate_key(func.__name__, *args, **kwargs)}"
            
            # Try to get from cache
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            await self.cache_manager.set(cache_key, result, self.ttl)
            return result
        
        return wrapper

class HTSDataCache:
    """Specialized cache for HTS data"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.hts_prefix = "hts"
        self.search_prefix = "search"
        self.tariff_prefix = "tariff"
    
    async def get_hts_code(self, hts_code: str) -> Optional[Dict]:
        """Get HTS code from cache"""
        key = f"{self.hts_prefix}:code:{hts_code}"
        return await self.cache_manager.get(key)
    
    async def set_hts_code(self, hts_code: str, data: Dict, ttl: int = 86400) -> bool:
        """Set HTS code in cache (24 hour TTL)"""
        key = f"{self.hts_prefix}:code:{hts_code}"
        return await self.cache_manager.set(key, data, ttl)
    
    async def get_search_results(self, query: str, limit: int) -> Optional[List[Dict]]:
        """Get search results from cache"""
        key = f"{self.search_prefix}:{self.cache_manager.generate_key(query, limit)}"
        return await self.cache_manager.get(key)
    
    async def set_search_results(self, query: str, limit: int, results: List[Dict], ttl: int = 3600) -> bool:
        """Set search results in cache (1 hour TTL)"""
        key = f"{self.search_prefix}:{self.cache_manager.generate_key(query, limit)}"
        return await self.cache_manager.set(key, results, ttl)
    
    async def get_tariff_rate(self, hts_code: str, country: str) -> Optional[float]:
        """Get tariff rate from cache"""
        key = f"{self.tariff_prefix}:rate:{hts_code}:{country}"
        return await self.cache_manager.get(key)
    
    async def set_tariff_rate(self, hts_code: str, country: str, rate: float, ttl: int = 86400) -> bool:
        """Set tariff rate in cache (24 hour TTL)"""
        key = f"{self.tariff_prefix}:rate:{hts_code}:{country}"
        return await self.cache_manager.set(key, rate, ttl)
    
    async def invalidate_hts_data(self, hts_code: str) -> None:
        """Invalidate all cache entries for an HTS code"""
        pattern = f"{self.hts_prefix}:code:{hts_code}"
        await self._delete_pattern(pattern)
    
    async def invalidate_search_cache(self) -> None:
        """Invalidate all search cache entries"""
        pattern = f"{self.search_prefix}:*"
        await self._delete_pattern(pattern)
    
    async def _delete_pattern(self, pattern: str) -> None:
        """Delete keys matching pattern"""
        try:
            keys = await self.cache_manager.redis.keys(pattern)
            if keys:
                await self.cache_manager.redis.delete(*keys)
        except Exception as e:
            logger.error(f"Error deleting pattern {pattern}: {e}")

class SessionCache:
    """Session management with Redis"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.session_prefix = "session"
        self.session_ttl = 3600  # 1 hour
    
    async def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data"""
        key = f"{self.session_prefix}:{session_id}"
        return await self.cache_manager.get(key)
    
    async def set_session(self, session_id: str, data: Dict, ttl: Optional[int] = None) -> bool:
        """Set session data"""
        key = f"{self.session_prefix}:{session_id}"
        ttl = ttl or self.session_ttl
        return await self.cache_manager.set(key, data, ttl)
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete session"""
        key = f"{self.session_prefix}:{session_id}"
        return await self.cache_manager.delete(key)
    
    async def extend_session(self, session_id: str, ttl: Optional[int] = None) -> bool:
        """Extend session TTL"""
        key = f"{self.session_prefix}:{session_id}"
        ttl = ttl or self.session_ttl
        return await self.cache_manager.expire(key, ttl) 