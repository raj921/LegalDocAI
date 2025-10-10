from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-1.5-flash"
    GEMINI_EMBEDDING_MODEL: str = "models/text-embedding-004"
    EXA_API_KEY: str = ""
    DATABASE_URL: str = "sqlite:///./legal_templates.db"
    UPLOAD_DIR: str = "uploads"
    TEMPLATES_DIR: str = "templates_storage"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024
    CHUNK_SIZE: int = 8000
    CHUNK_OVERLAP: int = 500
    MIN_CONFIDENCE_THRESHOLD: float = 0.7
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
