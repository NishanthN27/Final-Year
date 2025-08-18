# src/interview_system/config/auth_config.py
from pydantic_settings import BaseSettings

class AuthSettings(BaseSettings):
    JWT_SECRET_KEY: str
    # Add other auth-related settings here later

    class Config:
        env_file = ".env"
        extra = 'ignore'

settings = AuthSettings()