"""
Configuration settings for TariffAI Backend
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    # Application settings
    app_name: str = "TariffAI Backend"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # Database settings
    database_url: str = Field(default="sqlite:///./tariff_ai.db")
    
    # ChromaDB settings
    chroma_db_path: str = Field(default="./data/chroma", env="CHROMA_DB_PATH")
    embedding_model_name: str = Field(default="all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    
    # Excel data settings
    excel_data_path: str = Field(default="./data/tariff_database_2025.xlsx", env="EXCEL_DATA_PATH")
    
    # API settings
    api_v1_prefix: str = Field(default="/api/v1")
    cors_origins: list = Field(default=["*"], env="CORS_ORIGINS")
    project_name: str = Field(default="TariffAI")
    version: str = Field(default="1.0.0")
    
    # Security settings
    secret_key: str = Field(default="your-secret-key-here")
    access_token_expire_minutes: int = Field(default=30)
    
    # Logging settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="./logs/app.log", env="LOG_FILE")
    
    # Ollama settings
    ollama_base_url: str = Field(default="http://localhost:11434")
    ollama_model: str = Field(default="llama3.1:latest", env="OLLAMA_MODEL")
    
    # External APIs
    openai_api_key: Optional[str] = Field(default=None)
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create settings instance
settings = Settings()

# Ensure required directories exist
def ensure_directories():
    """Create required directories if they don't exist"""
    directories = [
        Path("./data"),
        Path("./data/chroma"),
        Path("./logs"),
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# Initialize directories on import
ensure_directories() 