"""Database initialization and connection management"""

import os

from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL - production ready
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database/noxsuite.db")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Database dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables"""
    # Import models to register them
    from . import user

    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
