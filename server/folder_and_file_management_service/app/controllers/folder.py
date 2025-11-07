# app/controllers/folder.py
from sqlmodel import Session, select
from fastapi import HTTPException, status

from app.models.folder import FolderDB
from app.schemas.folder import FolderCreate, FolderRead, FolderUpdate


def create_folder_logic(folder_in: FolderCreate, db: Session) -> FolderRead:
    db_folder = FolderDB(**folder_in.model_dump())
    db.add(db_folder)
    db.commit()
    db.refresh(db_folder)
    return FolderRead.from_orm(db_folder)


def get_folder_logic(folder_id: int, db: Session) -> FolderRead:
    stmt = select(FolderDB).where(FolderDB.id == folder_id)
    db_folder = db.exec(stmt).first()
    if not db_folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    return FolderRead.from_orm(db_folder)


def list_folders_logic(db: Session, skip: int = 0, limit: int = 100) -> list[FolderRead]:
    stmt = select(FolderDB).offset(skip).limit(limit)
    folders = db.exec(stmt).all()
    return [FolderRead.from_orm(f) for f in folders]


def update_folder_logic(folder_id: int, folder_up: FolderUpdate, db: Session) -> FolderRead:
    db_folder = db.get(FolderDB, folder_id)
    if not db_folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    data = folder_up.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(db_folder, k, v)
    
    db.add(db_folder)
    db.commit()
    db.refresh(db_folder)
    return FolderRead.from_orm(db_folder)


def delete_folder_logic(folder_id: int, db: Session):
    db_folder = db.get(FolderDB, folder_id)
    if not db_folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    db.delete(db_folder)
    db.commit()