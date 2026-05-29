from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./freediary.db"
    SECRET_KEY: str = "freediary-dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    CORS_ORIGINS_STR: str = "http://localhost:3000"  # 👈 временное поле
    
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN: str | None = None
    TELEGRAM_BOT_NAME: str = "FreeDiaryBot"
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Преобразует строку с CORS_ORIGINS в список"""
        return [origin.strip() for origin in self.CORS_ORIGINS_STR.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()