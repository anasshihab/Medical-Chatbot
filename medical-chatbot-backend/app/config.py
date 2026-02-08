"""Application configuration using Pydantic Settings"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    DATABASE_URL: str
    
    # JWT Configuration
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    
    # OpenAI Configuration
    # تم تحميل مفتاح OpenAI من ملف .env — لا تضعه داخل الكود
    # OpenAI API key is loaded from .env file — do NOT put it in code
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    
    # WebTeb Symptom Checker API
    # مطلوب: احصل على بيانات API من WebTeb
    WEBTEB_API_KEY: str = ""
    WEBTEB_API_URL: str = "https://api.webteb.com/symptom-checker"
    
    # Application Settings
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    CORS_ORIGINS: str = "*"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# Global settings instance
settings = Settings()
