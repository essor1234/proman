from sqlmodel import SQLModel, create_engine, Session
from pathlib import Path

DB_DIR = Path("/app/data")
DB_DIR.mkdir(exist_ok=True)
"""CAUTION: I just change the dir of the database on 11.11.2025. 
Use this new version incase of solving confilcts.
--Essor--

"""
SQLITE_URL = f"sqlite:////data/account.db"

engine = create_engine(SQLITE_URL, echo=True)  # SEE SQL LOGS

def init_db():
    print("Creating tables...")
    SQLModel.metadata.create_all(engine)
    print("Tables created!")