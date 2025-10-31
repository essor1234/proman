# app/main.py
from fastapi import FastAPI, Depends
from app.core.database import create_db_and_tables, get_db  # Your database.py
from app.models.file import FileDB  # Import to register the table with SQLModel.metadata
from app.routes.file import router as file_router  # Your routes/file.py

app = FastAPI(title="File API Test", version="1.0")

# Create DB and tables on startup
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Your existing root endpoint
@app.get("/")
def read_root():
    return {"message": "Hello World"}

# Include file routes (prefix for organization)
app.include_router(file_router, prefix="/api/v1")

# Simple health check to test DB connection
@app.get("/health")
def health(db=Depends(get_db)):
    # Quick query to verify table exists and DB works
    count = db.exec(db.select(FileDB).count()).first()
    return {"status": "healthy", "db_connected": True, "files_count": count or 0}