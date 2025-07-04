"""
Core configuration for TariffAI
"""
import os
from pathlib import Path
from typing import Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "TariffAI - Intelligent HTS & Tariff Management"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/tariff_ai.db",
        env="DATABASE_URL"
    )
    
    # AI/ML
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        env="OLLAMA_BASE_URL"
    )
    ollama_model: str = Field(
        default="llama3.2:3b",
        env="OLLAMA_MODEL"
    )
    
    # Vector Database
    chroma_db_path: str = Field(
        default="./data/chroma",
        env="CHROMA_DB_PATH"
    )
    
    # Data
    tariff_data_path: str = Field(
        default="./data/tariff_database_2025.xlsx",
        env="TARIFF_DATA_PATH"
    )
    
    # External APIs
    serp_api_key: Optional[str] = Field(default=None, env="SERP_API_KEY")
    currency_api_key: Optional[str] = Field(default=None, env="CURRENCY_API_KEY")
    
    # CORS
    cors_origins: list = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        env="CORS_ORIGINS"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Ensure data directories exist
def ensure_directories():
    """Create necessary directories"""
    directories = [
        Path("./data"),
        Path("./data/chroma"),
        Path("./logs"),
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")


# Initialize directories on import
ensure_directories() 