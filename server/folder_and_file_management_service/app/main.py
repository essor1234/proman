# app/main.py
from fastapi import FastAPI, Depends
from sqlmodel import Session, select, func, SQLModel

from app.core.database import engine, get_db  # ← engine only

# IMPORT MODELS FIRST
from app.models.file import FileDB
from app.models.folder import FolderDB
from app.models.folderFile import FolderFileDB

from app.routes.file import router as file_router
from app.routes.folder import router as folder_router
from app.routes.folderFile import router as folder_file_router

app = FastAPI(title="ProMan", version="1.0")


# CREATE TABLES AFTER MODELS ARE IMPORTED
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)  # ← NOW it creates the file
    print(f"DB file: {engine.url}")


@app.get("/")
def read_root():
    return {"message": "ProMan API", "docs": "/docs"}


app.include_router(file_router, prefix="/api/v1")
app.include_router(folder_router, prefix="/api/v1")
app.include_router(folder_file_router, prefix="/api/v1")


@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        file_cnt = db.exec(select(func.count()).select_from(FileDB)).one()
        folder_cnt = db.exec(select(func.count()).select_from(FolderDB)).one()
        link_cnt = db.exec(select(func.count()).select_from(FolderFileDB)).one()
        return {
            "status": "healthy",
            "files": file_cnt,
            "folders": folder_cnt,
            "links": link_cnt,
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@app.get("/debug/db-path")
def debug_db_path():
    import os
    path = "/app/folder_and_file.db"
    return {
        "current_directory": os.getcwd(),
        "db_file_exists": os.path.exists(path),
        "db_file_path": os.path.abspath(path),
        "database_url": str(engine.url),
    }