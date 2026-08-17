import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # The database URL to connect to PostgreSQL
    DATABASE_URL: str
    
    # Secret key used to sign JWT access tokens
    SECRET_KEY: str
    
    # The cryptographic algorithm for JWT encoding
    ALGORITHM: str = "HS256"
    
    # Expiration time for access tokens in minutes
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Pydantic Configuration setting to specify the environment file
    # We look for '.env' relative to the execution directory
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore" # Ignore extra env variables not defined in our settings class
    )

# Instantiate the settings object to be imported by other files
settings = Settings()
