# app/core/database.py
from sqlmodel import create_engine, Session
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./folder_and_file.db")

engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL.lower() else {}
)

def get_db() -> Session: # type: ignore
    with Session(engine) as session:
        yield session