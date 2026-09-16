"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_ENV: str = "development"
    APP_NAME: str = "Border Document Screening Platform"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "insecure-dev-secret-key-replace-in-production-min-32-chars"

    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    POSTGRES_USER: str = "screening_admin"
    POSTGRES_PASSWORD: str = "screening_dev_password"
    POSTGRES_DB: str = "border_screening"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = "postgresql+psycopg://screening_admin:screening_dev_password@localhost:5432/border_screening"

    STORAGE_PROVIDER: str = "local"
    STORAGE_ENDPOINT: str = "http://localhost:9000"
    STORAGE_ACCESS_KEY: str = "minioadmin"
    STORAGE_SECRET_KEY: str = "minioadmin"
    STORAGE_BUCKET_DOCUMENTS: str = "screening-documents"
    STORAGE_SECURE: bool = False

    FACE_SIMILARITY_THRESHOLD: float = 0.75
    MIN_IMAGE_DPI: int = 300
    EXTERNAL_REGISTRY_PROVIDER: str = "mock"

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
