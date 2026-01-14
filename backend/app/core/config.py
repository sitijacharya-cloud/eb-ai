"""Application configuration using Pydantic settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pathlib import Path
import os

# Get the project root directory (3 levels up from this file)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """Application settings."""
    
    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-5.2"
    openai_embedding_model: str = "text-embedding-3-small"
    openai_temperature: float = 0.4
    
    # MySQL Configuration
    mysql_host: str = "localhost"
    mysql_user: str = "root"
    mysql_password: str = "Nepal@2001"
    mysql_database: str = "vector_db"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_title: str = "EB Estimation Agent API"
    api_version: str = "1.0.0"
    
    # External API (Future)
    external_estimate_api_url: str = "https://api.example.com/estimates"
    external_api_key: str = ""
    
    # Logging
    log_level: str = "INFO"
    
    # Retrieval Configuration
    similarity_top_k: int = 5
    similarity_threshold: float = 0.8
    
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra='ignore'
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
