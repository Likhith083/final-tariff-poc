"""
Enhanced Database Configuration with Performance Optimizations
Connection pooling, caching, and async optimizations for ATLAS Enterprise.
"""

import asyncio
import json
from typing import Any, Dict, Optional, List, AsyncGenerator
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from pathlib import Path
import os

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import QueuePool
from sqlalchemy import event, text
import chromadb
from chromadb.config import Settings as ChromaSettings
from fastapi import Depends

from .config import settings
from .logging import get_logger

logger = get_logger(__name__)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class DatabaseManager:
    """Enhanced database manager with connection pooling and caching."""
    
    def __init__(self):
        """Initialize database manager."""
        self.engine = None
        self.session_factory = None
        self.redis_client = None
        self.chroma_client = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize all database connections with optimizations."""
        if self._initialized:
            return
        
        # PostgreSQL with connection pooling
        if settings.database_url.startswith("postgresql"):
            self.engine = create_async_engine(
                settings.database_url,
                echo=settings.debug,
                connect_args={
                    "server_settings": {
                        "application_name": "atlas_enterprise",
                        "jit": "off"
                    }
                }
            )
        else:
            # For SQLite and others, do not pass server_settings
            self.engine = create_async_engine(
                settings.database_url,
                echo=settings.debug
            )
        
        # Add connection event listeners for monitoring
        @event.listens_for(self.engine.sync_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """Set database pragmas for performance."""
            if "sqlite" in str(self.engine.url):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.execute("PRAGMA cache_size=10000")
                cursor.execute("PRAGMA temp_store=MEMORY")
                cursor.close()
        
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Redis for caching with connection pooling
        self.redis_client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=50,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )
        
        # ChromaDB for vector storage
        self.chroma_client = chromadb.PersistentClient(
            path=os.path.join(settings.data_dir, "chroma"),
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        self._initialized = True
        logger.info("Database manager initialized with connection pooling")
    
    async def close(self):
        """Close all database connections."""
        if self.engine:
            await self.engine.dispose()
        if self.redis_client:
            await self.redis_client.close()
        logger.info("Database connections closed")
    
    @asynccontextmanager
    async def get_session(self):
        """Get database session with automatic cleanup."""
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all database connections."""
        health = {
            "timestamp": datetime.now().isoformat(),
            "postgresql": {"status": "unknown", "response_time": None},
            "redis": {"status": "unknown", "response_time": None},
            "chromadb": {"status": "unknown", "response_time": None}
        }
        
        # PostgreSQL health check
        try:
            start_time = datetime.now()
            async with self.get_session() as session:
                result = await session.execute(text("SELECT 1"))
                result.fetchone()
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            health["postgresql"] = {"status": "healthy", "response_time": f"{response_time:.2f}ms"}
        except Exception as e:
            health["postgresql"] = {"status": "unhealthy", "error": str(e)}
        
        # Redis health check
        try:
            start_time = datetime.now()
            await self.redis_client.ping()
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            health["redis"] = {"status": "healthy", "response_time": f"{response_time:.2f}ms"}
        except Exception as e:
            health["redis"] = {"status": "unhealthy", "error": str(e)}
        
        # ChromaDB health check
        try:
            start_time = datetime.now()
            self.chroma_client.heartbeat()
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            health["chromadb"] = {"status": "healthy", "response_time": f"{response_time:.2f}ms"}
        except Exception as e:
            health["chromadb"] = {"status": "unhealthy", "error": str(e)}
        
        return health


class CacheManager:
    """Advanced caching manager with Redis."""
    
    def __init__(self, redis_client: redis.Redis):
        """Initialize cache manager."""
        self.redis = redis_client
        self.default_ttl = 3600  # 1 hour
    
    async def get(self, key: str) -> Optional[Any]:
        """Get cached value."""
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.warning(f"Cache get error for key {key}: {e}")
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set cached value with TTL."""
        try:
            ttl = ttl or self.default_ttl
            serialized_value = json.dumps(value, default=str)
            await self.redis.setex(key, ttl, serialized_value)
            return True
        except Exception as e:
            logger.warning(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete cached value."""
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Cache delete error for key {key}: {e}")
            return False
    
    async def get_or_set(self, key: str, func, ttl: Optional[int] = None) -> Any:
        """Get cached value or set if not exists."""
        value = await self.get(key)
        if value is not None:
            return value
        
        # Generate new value
        if asyncio.iscoroutinefunction(func):
            value = await func()
        else:
            value = func()
        
        await self.set(key, value, ttl)
        return value
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern."""
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
                return len(keys)
        except Exception as e:
            logger.warning(f"Cache invalidation error for pattern {pattern}: {e}")
        return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            info = await self.redis.info("memory")
            return {
                "used_memory": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "total_commands_processed": info.get("total_commands_processed"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": (
                    info.get("keyspace_hits", 0) / 
                    max(info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1)
                ) * 100
            }
        except Exception as e:
            logger.warning(f"Failed to get cache stats: {e}")
            return {}


class VectorStore:
    """Enhanced vector store manager for knowledge base."""
    
    def __init__(self, chroma_client: chromadb.Client):
        """Initialize vector store."""
        self.client = chroma_client
        self.collections = {}
    
    def get_or_create_collection(self, name: str) -> chromadb.Collection:
        """Get or create a ChromaDB collection."""
        if name not in self.collections:
            self.collections[name] = self.client.get_or_create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"}
            )
        return self.collections[name]
    
    async def add_document(self, collection_name: str, document: str, 
                          metadata: Dict[str, Any], doc_id: str) -> bool:
        """Add document to vector store."""
        try:
            collection = self.get_or_create_collection(collection_name)
            collection.add(
                documents=[document],
                metadatas=[metadata],
                ids=[doc_id]
            )
            return True
        except Exception as e:
            logger.error(f"Failed to add document to vector store: {e}")
            return False
    
    async def search_documents(self, collection_name: str, query: str, 
                             n_results: int = 5) -> List[Dict[str, Any]]:
        """Search documents in vector store."""
        try:
            collection = self.get_or_create_collection(collection_name)
            results = collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            documents = []
            for i, doc in enumerate(results["documents"][0]):
                documents.append({
                    "content": doc,
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                    "id": results["ids"][0][i]
                })
            
            return documents
        except Exception as e:
            logger.error(f"Failed to search vector store: {e}")
            return []
    
    async def update_document(self, collection_name: str, doc_id: str, 
                            document: str, metadata: Dict[str, Any]) -> bool:
        """Update document in vector store."""
        try:
            collection = self.get_or_create_collection(collection_name)
            collection.update(
                ids=[doc_id],
                documents=[document],
                metadatas=[metadata]
            )
            return True
        except Exception as e:
            logger.error(f"Failed to update document in vector store: {e}")
            return False
    
    async def delete_document(self, collection_name: str, doc_id: str) -> bool:
        """Delete document from vector store."""
        try:
            collection = self.get_or_create_collection(collection_name)
            collection.delete(ids=[doc_id])
            return True
        except Exception as e:
            logger.error(f"Failed to delete document from vector store: {e}")
            return False


# Global database manager instance
db_manager = DatabaseManager()
cache_manager = None
vector_store = None

async def init_database():
    """Initialize database connections."""
    global cache_manager, vector_store
    
    await db_manager.initialize()
    cache_manager = CacheManager(db_manager.redis_client)
    vector_store = VectorStore(db_manager.chroma_client)
    
    logger.info("Database initialization completed")

async def close_database():
    """Close database connections."""
    await db_manager.close()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with db_manager.get_session() as session:
        yield session

def get_cache() -> CacheManager:
    """Get cache manager."""
    return cache_manager

def get_vector_store() -> VectorStore:
    """Get vector store."""
    return vector_store 