"""
Application configuration using Pydantic Settings
"""
from functools import lru_cache
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Server settings
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    debug: bool = Field(default=True, description="Debug mode")
    
    # CORS settings
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins"
    )
    
    # Database settings
    firebase_credentials_path: str = Field(
        default="firebase-service.json",
        description="Path to Firebase credentials JSON file"
    )
    
    # External services
    meilisearch_url: str = Field(default="http://localhost:7700", description="MeiliSearch URL")
    meilisearch_api_key: str = Field(default="", description="MeiliSearch API key")
    
    # Payment settings
    moysar_pk: str = Field(default="", description="Moysar public key")
    moysar_sk: str = Field(default="", description="Moysar secret key")
    
    # Security
    secret_key: str = Field(default="your-secret-key-change-in-production", description="JWT secret key")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiration")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()