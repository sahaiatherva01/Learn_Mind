from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    PROJECT_NAME: str = "Learn_Mind"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./learn_mind.db",
        description="Async database connection URL (Postgres or SQLite)",
    )

    # Supabase (optional integration when available)
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_KEY: str = ""

    # Security
    JWT_SECRET: str = "learn-mind-dev-secret-key-change-in-production-2026-min32chars"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*",
    ]

    # LLM Settings (for LLMClient)
    LLM_PROVIDER_KEYS: str = ""
    DEFAULT_LLM_PROVIDER: str = "mock"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
