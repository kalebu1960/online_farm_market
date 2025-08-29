"""Database configuration and session management."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment or use default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///farm_market.db")
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///test_farm_market.db")

# Determine if we're in test mode
TESTING = os.getenv("TESTING", "false").lower() == "true"

# Use test database if in testing mode
if TESTING:
    DATABASE_URL = TEST_DATABASE_URL
    # For SQLite in-memory testing
    if ":memory:" in DATABASE_URL:
        engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        engine = create_engine(DATABASE_URL)
else:
    engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db():
    """
    Dependency function to get DB session.
    Use this in your FastAPI route dependencies or other contexts.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize the database by creating all tables."""
    from . import models  # noqa: F401 - Import models to register them with Base
    Base.metadata.create_all(bind=engine)

def drop_db():
    """
    Drop all tables. Use with caution, especially in production!
    Primarily for testing and development.
    """
    Base.metadata.drop_all(bind=engine)

# For backward compatibility
BaseModel = Base
