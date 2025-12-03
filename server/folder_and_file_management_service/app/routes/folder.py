# app/routes/folder.py
from http.client import HTTPException
from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select

from app.core.database import get_db
from app.controllers.folder import (
    create_folder_logic,
    get_folder_logic,
    list_folders_logic,
    delete_folder_in_project,
    create_folder_in_project,
    update_folder_in_project
)
from app.schemas.folder import FolderCreate, FolderRead, FolderUpdate
from app.controllers.folder import create_folder_in_project, get_project_logic
from app.models.folder import FolderDB
from app.models.folderManager import FolderManager

from app.routes.security import get_current_user_id



router = APIRouter(prefix="/folders", tags=["folders"])


@router.post("/{folder_id}/share/project/{projectid}", status_code=201)
def share_folder_with_project(
    folder_id: int,
    projectid: str,
    db: Session = Depends(get_db)
):
    # Validate both exist
    from app.controllers.folder import get_folder_logic
    get_folder_logic(folder_id, db)
    get_project_logic(projectid)

    # Prevent duplicate
    exists = db.exec(
        select(FolderManager).where(
            FolderManager.folderId == folder_id,
            FolderManager.projectid == projectid
        )
    ).first()
    if exists:
        raise HTTPException(400, "Folder already in project")

    link = FolderManager(folderId=folder_id, projectid=projectid)
    db.add(link)
    db.commit()
    return {"message": "Folder shared successfully"}

@router.post("/project/{projectid}", response_model=FolderRead, status_code=status.HTTP_201_CREATED)
def create_folder(
    projectid: str,
    folder_data: FolderCreate,
    user_id: int = Depends(get_current_user_id),  # Get authenticated user
    db: Session = Depends(get_db)
):
    return create_folder_in_project(folder_data, projectid, user_id, db)

@router.get("/project/{projectid}", response_model=list[FolderRead])
def get_folders_in_project(projectid: str, db: Session = Depends(get_db)):
    # Validate project exists
    get_project_logic(projectid)

    stmt = (
        select(FolderDB)
        .join(FolderManager)
        .where(FolderManager.projectid == projectid)
    )
    folders = db.exec(stmt).all()
    return [FolderRead.from_orm(f) for f in folders]


# @router.post("/", response_model=FolderRead, status_code=status.HTTP_201_CREATED)
# def create_folder(folder_in: FolderCreate, db=Depends(get_db)):
#     return create_folder_logic(folder_in, db)

"""
READ FOLDER LOGIC

"""
@router.get("/{folder_id}", response_model=FolderRead)
def read_folder(folder_id: int, db=Depends(get_db)):
    return get_folder_logic(folder_id, db)


@router.get("/", response_model=list[FolderRead])
def list_folders(user_id: int = Depends(get_current_user_id), skip: int = 0, limit: int = 100, db=Depends(get_db)):
    return list_folders_logic(user_id, db, skip, limit)

"""
UPDATE FOLDER LOGIC

"""
@router.patch("/project/{projectid}/folder/{folder_id}")
def update_folder(
    folder_id: int,
    projectid: str,           # ← required!
    folder_up: FolderUpdate,
    db: Session = Depends(get_db)
):
    return update_folder_in_project(folder_id, folder_up, projectid, db)

"""
DELETE FOLDER LOGIC
"""

@router.delete("/project/{projectid}/folder/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_folder(
    folder_id: int,
    projectid: str,           # ← required!
    db: Session = Depends(get_db)
):
    return delete_folder_in_project(folder_id, projectid, db)