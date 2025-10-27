# app/routes/file.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.core.database import get_db
from app.schemas.file import FileCreate, FileRead
from app.models.file import FileDB

router = APIRouter()

@router.post("/files/", response_model=FileRead)
def create_file(file_in: FileCreate, db: Session = Depends(get_db)):
    # Validate via FileCreate, map to DB model
    db_file = FileDB(**file_in.dict())
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file  # Auto-serializes to FileRead

@router.get("/files/{file_id}", response_model=FileRead)
def read_file(file_id: int, db: Session = Depends(get_db)):
    db_file = db.get(FileDB, file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    return db_file

@router.get("/files/", response_model=list[FileRead])
def list_files(db: Session = Depends(get_db)):
    files = db.exec(select(FileDB)).all()
    return files