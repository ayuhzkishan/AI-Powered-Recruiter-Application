from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Optional
import json


class Settings(BaseSettings):
    APP_ENV: str = "development"
    SECRET_KEY: str  # Required — fails loudly if missing
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    DATABASE_URL: str
    GEMINI_API_KEY: Optional[str] = None
    AI_MODEL: str = "gemini-1.5-flash"

    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 5

    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    RATE_LIMIT_UPLOAD: str = "10/minute"
    RATE_LIMIT_API: str = "100/minute"

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v):
        """Accept JSON array, comma-separated string, or plain string."""
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("["):
                return json.loads(v)
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
