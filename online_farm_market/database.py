from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from .config import settings

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Enable connection health checks
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Create a scoped session factory
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

# Base class for all models
Base = declarative_base()

def get_db():
    ""
    Dependency function to get a database session.
    Use this in FastAPI route dependencies.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    ""
    Initialize the database by creating all tables.
    This should be called during application startup.
    """
    from .models import Base
    Base.metadata.create_all(bind=engine)

def drop_db():
    ""
    Drop all tables in the database.
    WARNING: This will delete all data!
    """
    from .models import Base
    Base.metadata.drop_all(bind=engine)

# Import models to ensure they are registered with SQLAlchemy
from .models import User, Customer, Farmer, Product, Order, OrderItem  # noqa
