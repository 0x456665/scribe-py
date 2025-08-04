from pydantic_settings import BaseSettings
from pydantic import Field
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL") or "sqlite+aiosqlite:///./test.db"
    MODEL: str = os.getenv("MODEL") or "base.en"
    # JWT Configuration
    SECRET_KEY: str = (
        os.getenv("SECRET_KEY") or "your-super-secret-key-change-this-in-production"
    )
    ALGORITHM: str = os.getenv("ALGORITHM") or "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES") or 15
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS") or 15)

    # File Upload
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE") or 50485760)  # 50MB
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR") or "./temp"
    # WHISPER_MODEL_PATH: str = Field(
    #     default="./models/ggml-base.en.bin", env="WHISPER_MODEL_PATH"
    # )

    # API Configuration
    API_V1_PREFIX: str = os.getenv("API_V1_PREFIX") or "/api/v1"
    DEBUG: bool = bool(os.getenv("DEBUG") or False)

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS") or 100)
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW") or 3600)

    class Config:
        env_file = ".env"


settings = Settings()
