import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # The database URL to connect to PostgreSQL or fallback SQLite
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./recruitflow.db")
    
    # Secret key used to sign JWT access tokens
    SECRET_KEY: str = os.getenv("SECRET_KEY", "recruitflow-super-secret-key-jwt-2026-prod")
    
    # The cryptographic algorithm for JWT encoding
    ALGORITHM: str = "HS256"
    
    # Expiration time for access tokens in minutes
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Pydantic Configuration setting to specify the environment file
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Instantiate the settings object to be imported by other files
settings = Settings()
