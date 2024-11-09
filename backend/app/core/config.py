from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "VAPT Scanner"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "postgresql://user_zkqsuwzsbe:U6wloqDMnlsgXbv1JHf8@devinapps-backend-prod.cluster-clussqewa0rh.us-west-2.rds.amazonaws.com/db_vtbtjhumuj?sslmode=require"

    # Security settings
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # CORS settings
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000"]

    # Scanner settings
    MAX_SCAN_DEPTH: int = 3
    SCAN_TIMEOUT: int = 300

    class Config:
        case_sensitive = True

settings = Settings()
