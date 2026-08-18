# backend/app/core/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/recruitflow")
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./backend/uploads")
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100 MB

settings = Settings()