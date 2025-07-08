"""
ATLAS Enterprise Configuration
Centralized configuration management using Pydantic v2 settings.
"""

import os
from typing import List, Optional, Union
from pydantic import Field, PostgresDsn, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Application
    app_name: str = "ATLAS Enterprise Tariff Strategist"
    app_version: str = "3.0.0"
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # Database - Allow any string for testing
    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/atlas.db",
        env="DATABASE_URL"
    )
    
    # Redis (for Celery)
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL"
    )
    
    # Security
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        env="CORS_ORIGINS"
    )
    
    # External APIs
    serp_api_key: Optional[str] = Field(default=None, env="SERP_API_KEY")
    
    # AI Services - Groq API
    groq_api_key: Optional[str] = Field(default=None, env="GROQ_API_KEY")
    
    # Groq Models for different purposes
    groq_chat_model: str = Field(default="llama3-70b-8192", env="GROQ_CHAT_MODEL")  # For chat/general
    groq_analysis_model: str = Field(default="mixtral-8x7b-32768", env="GROQ_ANALYSIS_MODEL")  # For analysis
    groq_fast_model: str = Field(default="llama3-8b-8192", env="GROQ_FAST_MODEL")  # For quick responses
    
    # Vector Store - ChromaDB (local)
    chroma_db_path: str = Field(default="./data/chroma", env="CHROMA_DB_PATH")
    chroma_collection_name: str = Field(default="atlas_documents", env="CHROMA_COLLECTION_NAME")
    
    # Tariff APIs
    usitc_api_url: str = Field(
        default="https://hts.usitc.gov/api",
        env="USITC_API_URL"
    )
    
    # Background Tasks
    celery_broker_url: str = Field(
        default="redis://localhost:6379/0",
        env="CELERY_BROKER_URL"
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/0",
        env="CELERY_RESULT_BACKEND"
    )
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = "json"  # json or text
    
    # File Storage
    upload_dir: str = Field(default="./uploads", env="UPLOAD_DIR")
    max_file_size: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    data_dir: str = Field(default="./data", env="DATA_DIR")
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    
    # Cache Settings
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")  # 1 hour
    
    @validator("cors_origins", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL for Alembic."""
        return str(self.database_url).replace("+asyncpg", "")


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Dependency to get settings instance."""
    return settings 