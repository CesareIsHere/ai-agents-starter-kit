from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Agents API"
    
    # API Keys e configurazioni
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/agents_db")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Cache settings
    CACHE_ENABLED: bool = True
    CACHE_EXPIRATION: int = 3600  # 1 ora
    
    class Config:
        env_file = ".env"

settings = Settings()
