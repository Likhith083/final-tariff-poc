from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # App settings
    app_name: str = "Tariff AI Backend"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Database settings
    database_url: str = "sqlite:///./tariff_ai.db"
    
    # Security settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # AI/LLM settings
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    ollama_timeout: int = 45  # Increase timeout for complex queries
    ollama_max_tokens: int = 800  # Reduce token limit for faster responses
    ollama_temperature: float = 0.2  # Lower temperature for more consistent responses
    
    # ChromaDB settings
    chroma_persist_directory: str = "./data/chroma"
    
    # CORS settings
    allowed_origins: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # File upload settings
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    upload_directory: str = "./uploads"
    
    # Logging settings
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create settings instance
settings = Settings()

# Ensure directories exist
os.makedirs(settings.upload_directory, exist_ok=True)
os.makedirs(os.path.dirname(settings.log_file), exist_ok=True)
os.makedirs(settings.chroma_persist_directory, exist_ok=True) 