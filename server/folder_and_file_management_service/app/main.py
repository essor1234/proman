# app/main.py
from fastapi import FastAPI, Depends
from sqlmodel import Session

from app.core.database import create_db_and_tables, get_db
from app.models.file import FileDB  # Ensures table is registered
from app.routes.file import router as file_router  # Your router

app = FastAPI(
    title="File API Test",
    version="1.0",
    description="A self-contained file management API using FastAPI + SQLModel + SQLite",
)


# ------------------------------------------------------------------
# Startup: Create DB + Tables
# ------------------------------------------------------------------
@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# ------------------------------------------------------------------
# Root Endpoint
# ------------------------------------------------------------------
@app.get("/")
def read_root():
    return {"message": "Hello World", "docs": "/docs"}


# ------------------------------------------------------------------
# Include File Routes under /api/v1
# ------------------------------------------------------------------
app.include_router(file_router, prefix="/api/v1")


# ------------------------------------------------------------------
# Health Check with DB Validation
# ------------------------------------------------------------------
@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        # Test query: count files
        count = db.exec(FileDB.select().with_only_columns([FileDB.count()])).first()
        return {
            "status": "healthy",
            "db_connected": True,
            "files_count": count or 0,
            "api_version": "v1",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "db_connected": False,
            "error": str(e),
        }