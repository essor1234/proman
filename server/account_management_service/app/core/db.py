from sqlmodel import SQLModel, create_engine
from pathlib import Path
import os

# Place the database inside the service directory (server/account_management_service/data)
BASE_DIR = Path(__file__).resolve().parents[2]
DB_DIR = BASE_DIR / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DB_DIR / "account.db"
# Use a file-based sqlite URL that works across platforms
SQLITE_URL = f"sqlite:///{DB_PATH.as_posix()}"

engine = create_engine(SQLITE_URL, echo=True)

def init_db():
    print("Creating tables...")
    SQLModel.metadata.create_all(engine)
    print("Tables created!")