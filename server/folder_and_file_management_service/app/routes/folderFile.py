# app/routes/folder_file.py
from fastapi import APIRouter, Depends, status
from typing import List

from app.core.database import get_db
from app.controllers.folderFile import (
    link_file_to_folder_logic,
    unlink_file_from_folder_logic,
    list_links_for_folder_logic,
    list_folders_for_file_logic,
)
from app.schemas.folderFile import FolderFileBase

router = APIRouter()


# -------------------------------------------------
# LINK / UNLINK
# -------------------------------------------------
@router.post(
    "/folders/{folder_id}/files/{file_id}",
    response_model=FolderFileBase,
    status_code=status.HTTP_201_CREATED,
    summary="Link a file to a folder"
)
def link_file(folder_id: int, file_id: int, db=Depends(get_db)):
    return link_file_to_folder_logic(folder_id, file_id, db)


@router.delete(
    "/folders/{folder_id}/files/{file_id}",
    status_code=status.HTTP_200_OK,
    summary="Unlink a file from a folder"
)
def unlink_file(folder_id: int, file_id: int, db=Depends(get_db)):
    return unlink_file_from_folder_logic(folder_id, file_id, db)


# -------------------------------------------------
# LIST LINKS
# -------------------------------------------------
@router.get(
    "/folders/{folder_id}/files",
    response_model=List[FolderFileBase],
    summary="List all files linked to a folder"
)
def list_folder_files(folder_id: int, db=Depends(get_db)):
    return list_links_for_folder_logic(folder_id, db)


@router.get(
    "/files/{file_id}/folders",
    response_model=List[FolderFileBase],
    summary="List all folders that contain a file"
)
def list_file_folders(file_id: int, db=Depends(get_db)):
    return list_folders_for_file_logic(file_id, db)