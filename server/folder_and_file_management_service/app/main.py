# app/main.py
from fastapi import FastAPI, Depends
from sqlmodel import Session, select, func, SQLModel

from app.core.database import engine, get_db  # ← engine only

# IMPORT MODELS FIRST
from app.models.file import FileDB
# from app.models.folder import FolderDB
from app.models.folderFile import FolderFileDB

from app.routes.file import router as file_router
from app.routes.folder import router as folder_router
from app.routes.folderFile import router as folder_file_router
from app.routes.testing import router as testing_router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="ProMan", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# CREATE TABLES AFTER MODELS ARE IMPORTED
@app.on_event("startup")
def on_startup():
    import pathlib
    pathlib.Path("/data").mkdir(parents=True, exist_ok=True)  # ← create if missing
    SQLModel.metadata.create_all(engine)
    print(f"DB ready → {engine.url}")


@app.get("/")
def read_root():
    return {"message": "ProMan API", "docs": "/docs"}


app.include_router(file_router, prefix="/api/v1")
app.include_router(folder_router, prefix="/api/v1")
app.include_router(folder_file_router, prefix="/api/v1")
app.include_router(testing_router, prefix="/api/v1")



# @app.get("/health")
# def health(db: Session = Depends(get_db)):
#     try:
#         file_cnt = db.exec(select(func.count()).select_from(FileDB)).one()
#         folder_cnt = db.exec(select(func.count()).select_from(FolderDB)).one()
#         link_cnt = db.exec(select(func.count()).select_from(FolderFileDB)).one()
#         return {
#             "status": "healthy",
#             "database": str(db.bind.url),   # ← ADD THIS
#             "files": file_cnt,
#             "folders": folder_cnt,
#             "links": link_cnt,
#         }
#     except Exception as e:
#         return {"status": "unhealthy", "error": str(e)}
    
    
@app.get("/debug/db-path")
def debug_db_path():
    import os
    url = str(engine.url)
    db_path = url.replace("sqlite://", "")  # → /data/folder_and_file.db
    return {
        "DATABASE_URL": os.getenv("DATABASE_URL"),
        "engine.url": url,
        "container_db_path": db_path,
        "exists_in_container": os.path.exists(db_path),
        "size_bytes": os.path.getsize(db_path) if os.path.exists(db_path) else None,
        "host_db_path": f"./data/{os.path.basename(db_path)}",  # ← correct
    }