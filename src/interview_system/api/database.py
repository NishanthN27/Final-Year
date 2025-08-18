# src/interview_system/api/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from interview_system.config.db_config import db_settings
from interview_system.models.base import Base
from sqlalchemy import create_engine
# Create the SQLAlchemy engine that will connect to the database
engine = create_engine(db_settings.DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_all_tables():
    """
    A utility function to create all database tables based on the models.
    """
    Base.metadata.create_all(bind=engine)

def get_db():
    """
    FastAPI dependency to get a database session.
    It ensures the database session is always closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()