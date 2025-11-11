from sqlmodel import SQLModel, create_engine, Session
from pathlib import Path

DB_DIR = Path("/app/data")
DB_DIR.mkdir(exist_ok=True)
SQLITE_URL = f"sqlite:///{DB_DIR}/app.db"

engine = create_engine(SQLITE_URL, echo=True)  # SEE SQL LOGS

def init_db():
    print("Creating tables...")
    SQLModel.metadata.create_all(engine)
    print("Tables created!")