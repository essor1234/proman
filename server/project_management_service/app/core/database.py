from typing import Generator  # For type hinting generator functions
from sqlalchemy import create_engine  # Creates DB connection engine
from sqlalchemy.orm import sessionmaker, declarative_base  # Session factory & base class

# Database URL: SQLite file-based DB (in-memory for dev, persistent file)
SQLALCHEMY_DATABASE_URL = "sqlite:////data/project.db"

# Create engine with SQLite-specific args (allows multi-thread access)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}  # Required for SQLite in FastAPI
)

# Session factory: Manages DB transactions (autocommit=False for explicit control)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class: All ORM models inherit from this
Base = declarative_base()

def get_db() -> Generator:
    """
    Dependency function for FastAPI.
    - Yields DB session to route
    - Auto-closes session after request (resource cleanup)
    """
    db = SessionLocal()  # Create new session per request
    try:
        yield db  # Pass to route handler
    finally:
        db.close()  # Always close, even on errors