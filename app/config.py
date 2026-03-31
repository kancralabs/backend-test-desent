"""Application configuration using Pydantic Settings"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    # Database Configuration
    database_url: str
    db_pool_size: int = 20
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_echo: bool = False

    # JWT Configuration
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # API Configuration
    api_v1_prefix: str = "/api/v1"
    project_name: str = "Books API - 8 Level Challenge"
    project_version: str = "1.0.0"


# Singleton instance
settings = Settings()
