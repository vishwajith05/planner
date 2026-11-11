from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "PlanWise AI"
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    DATABASE_URL: str = "sqlite:///./planwise.db"

    AI_PROVIDER: str = "mock"  # "mock" or "gemini"
    GEMINI_API_KEY: str = ""

    SECRET_KEY: str = "planwise-ai-super-secure-jwt-secret-key-32-chars-long-minimum-phase2"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
