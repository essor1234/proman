# app/core/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Get the DB URL from Docker Environment
# If not found, fallback to a local file for testing outside Docker
# Note: In Docker, this should look like "sqlite:////data/process.db"
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./process.db")

# 2. Configure arguments for SQLite
# "check_same_thread": False is needed only for SQLite
connect_args = {}
if "sqlite" in SQLALCHEMY_DATABASE_URL:
    connect_args = {"check_same_thread": False}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()