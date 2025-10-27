# app/core/database.py
from sqlmodel import SQLModel, create_engine, Session
import os

# Use env var for DB (Postgres in Docker, fallback to your SQLite file)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./folder&file.db")

# Sync engine
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Logs SQL queries (remove in prod)
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},  # SQLite threading fix only
)

# Function to create all tables (call in main.py)
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Dependency: Uses SQLModel's Session (has .exec() for queries)
def get_db() -> Session: # type: ignore
    with Session(engine) as session:  # Context-managed for auto-close
        yield session