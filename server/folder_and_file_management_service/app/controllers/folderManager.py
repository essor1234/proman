
from fastapi import HTTPException
from sqlmodel import Session
from app.models.folderManager import FolderManager
from app.schemas.folderManager import FolderManagerCreate, FolderManagerRead
from app.controllers.getProjectController import get_project_logic

def create_folder_manager_logic(
    folder_in: FolderManagerCreate,
    db: Session
) -> FolderManagerRead:
    
    # 1. Validate project exists
    get_project_logic(folder_in.projectid)  # ← raises 404 or 502 if invalid

    # 2. Create folder manager with validated projectid
    db_folder = FolderManager(
        folderId=folder_in.folderId,
        projectid=folder_in.projectid  # ← trusted because validated
    )

    db.add(db_folder)
    db.commit()
    db.refresh(db_folder)

    return FolderManagerRead.from_orm(db_folder)