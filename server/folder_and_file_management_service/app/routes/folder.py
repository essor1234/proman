# app/routes/folder.py
from fastapi import APIRouter, Depends, status

from app.core.database import get_db
from app.controllers.folder import (
    create_folder_logic,
    get_folder_logic,
    list_folders_logic,
    update_folder_logic,
    delete_folder_logic,
)
from app.schemas.folder import FolderCreate, FolderRead, FolderUpdate

router = APIRouter(prefix="/folders", tags=["folders"])


@router.post("/", response_model=FolderRead, status_code=status.HTTP_201_CREATED)
def create_folder(folder_in: FolderCreate, db=Depends(get_db)):
    return create_folder_logic(folder_in, db)


@router.get("/{folder_id}", response_model=FolderRead)
def read_folder(folder_id: int, db=Depends(get_db)):
    return get_folder_logic(folder_id, db)


@router.get("/", response_model=list[FolderRead])
def list_folders(skip: int = 0, limit: int = 100, db=Depends(get_db)):
    return list_folders_logic(db, skip, limit)


@router.patch("/{folder_id}", response_model=FolderRead)
def update_folder(folder_id: int, folder_up: FolderUpdate, db=Depends(get_db)):
    return update_folder_logic(folder_id, folder_up, db)


@router.delete("/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_folder(folder_id: int, db=Depends(get_db)):
    delete_folder_logic(folder_id, db)