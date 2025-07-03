"""
Configuration management for TariffAI
Consolidated configuration combining the best approaches from all projects.
"""

import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    app_name: str = "TariffAI"
    app_version: str = "1.0.0"
    environment: str = Field(default="development", env="ENVIRONMENT")
    is_development: bool = Field(default=True, env="IS_DEVELOPMENT")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        env="CORS_ORIGINS"
    )
    
    # Database
    chroma_db_path: str = Field(
        default="./data/chroma",
        env="CHROMA_DB_PATH"
    )
    
    # Data
    data_dir: str = Field(
        default="./data",
        env="DATA_DIR"
    )
    excel_data_path: str = Field(
        default="./data/tariff_database_2025.xlsx",
        env="EXCEL_DATA_PATH"
    )
    
    # AI/LLM
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        env="OLLAMA_BASE_URL"
    )
    ollama_host: str = Field(
        default="http://localhost:11434",
        env="OLLAMA_HOST"
    )
    ollama_model: str = Field(
        default="llama3.2:3b",
        env="OLLAMA_MODEL"
    )
    
    # Embedding Model
    embedding_model_name: str = Field(
        default="all-MiniLM-L6-v2",
        env="EMBEDDING_MODEL"
    )
    
    # Search
    search_limit: int = Field(default=10, env="SEARCH_LIMIT")
    search_threshold: float = Field(default=0.7, env="SEARCH_THRESHOLD")
    
    # Currency
    currency_api_key: Optional[str] = Field(default=None, env="CURRENCY_API_KEY")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Security
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    
    # Cache
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")  # 1 hour
    
    # Monitoring
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings


# Environment-specific configurations
class DevelopmentSettings(Settings):
    """Development environment settings."""
    environment: str = "development"
    is_development: bool = True
    log_level: str = "DEBUG"
    cors_origins: List[str] = ["*"]


class ProductionSettings(Settings):
    """Production environment settings."""
    environment: str = "production"
    is_development: bool = False
    log_level: str = "WARNING"
    cors_origins: List[str] = [
        "https://yourdomain.com",
        "https://www.yourdomain.com"
    ]


class TestingSettings(Settings):
    """Testing environment settings."""
    environment: str = "testing"
    is_development: bool = True
    log_level: str = "DEBUG"
    cors_origins: List[str] = ["*"]
    chroma_db_path: str = "./data/chroma_test"


def get_environment_settings() -> Settings:
    """Get environment-specific settings."""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings() 