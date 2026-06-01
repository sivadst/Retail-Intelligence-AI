"""Retail Intelligence AI Backend Configuration"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    app_name: str = "Retail Intelligence AI V2"
    environment: str = "development"
    debug: bool = True

    # Database
    database_url: str
    clickhouse_url: str = "clickhouse://default@localhost:9000/retail_intelligence"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4o"

    # S3 / Storage
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_s3_bucket: str = "retail-intelligence-datasets"
    aws_s3_region: str = "us-east-1"
    use_local_storage: bool = True

    # Email
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    admin_email: str = "admin@retailintelligence.com"

    # URLs
    backend_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"

    # Logging
    log_level: str = "INFO"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
