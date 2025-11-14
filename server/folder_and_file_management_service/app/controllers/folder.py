from sqlmodel import Session, select
from fastapi import HTTPException
from ..models.folder import FolderDB
from app.schemas.folder import FolderCreate, FolderRead, FolderUpdate
from app.models.folderManager import FolderManager
from app.controllers.getProjectController import get_project_logic

def create_folder_in_project(
    folder_data: FolderCreate,
    projectid: str,
    db: Session
) -> FolderRead:
    # 1. Validate project exists
    get_project_logic(projectid)

    # 2. Create folder — IGNORE user-provided id
    folder_dict = folder_data.model_dump(exclude={"id"})
    db_folder = FolderDB(**folder_dict)  # ← id = None → DB auto-generates

    db.add(db_folder)
    db.commit()
    db.refresh(db_folder)

    # 3. Link folder to project
    link = FolderManager(folderId=db_folder.id, projectid=projectid)
    db.add(link)
    db.commit()

    return FolderRead.from_orm(db_folder)

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