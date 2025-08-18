# src/interview_system/config/db_config.py
from pydantic_settings import BaseSettings

class DatabaseSettings(BaseSettings):
    DATABASE_URL: str

    class Config:
        env_file = ".env"
        extra = 'ignore'

db_settings = DatabaseSettings()