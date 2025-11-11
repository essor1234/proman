# app/controllers/folder_file.py
from sqlmodel import Session, select
from fastapi import HTTPException, status

from app.models.folderFile import FolderFileDB
from app.models.folder import FolderDB
from app.models.file import FileDB
from app.schemas.folderFile import FolderFileBase


def _check_folder_exists(folder_id: int, db: Session) -> FolderDB:
    folder = db.get(FolderDB, folder_id)
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    return folder


def _check_file_exists(file_id: int, db: Session) -> FileDB:
    file = db.get(FileDB, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return file


def link_file_to_folder_logic(folder_id: int, file_id: int, db: Session) -> FolderFileBase:
    _check_folder_exists(folder_id, db)
    _check_file_exists(file_id, db)

    # idempotent – already linked?
    exists = db.exec(
        select(FolderFileDB).where(
            (FolderFileDB.folderId == folder_id) & (FolderFileDB.fileId == file_id)
        )
    ).first()
    if exists:
        raise HTTPException(status_code=409, detail="File already linked to folder")

    link = FolderFileDB(folderId=folder_id, fileId=file_id)
    db.add(link)
    db.commit()
    db.refresh(link)
    return FolderFileBase.from_orm(link)


def unlink_file_from_folder_logic(folder_id: int, file_id: int, db: Session):
    link = db.exec(
        select(FolderFileDB).where(
            (FolderFileDB.folderId == folder_id) & (FolderFileDB.fileId == file_id)
        )
    ).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    db.delete(link)
    db.commit()
    return {"detail": "Unlinked successfully"}


def list_links_for_folder_logic(folder_id: int, db: Session) -> list[FolderFileBase]:
    _check_folder_exists(folder_id, db)
    links = db.exec(select(FolderFileDB).where(FolderFileDB.folderId == folder_id)).all()
    return [FolderFileBase.from_orm(l) for l in links]


def list_folders_for_file_logic(file_id: int, db: Session) -> list[FolderFileBase]:
    _check_file_exists(file_id, db)
    links = db.exec(select(FolderFileDB).where(FolderFileDB.fileId == file_id)).all()
    return [FolderFileBase.from_orm(l) for l in links]