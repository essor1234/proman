from sqlmodel import Session, select
from fastapi import HTTPException
from ..models.folder import FolderDB
from app.schemas.folder import FolderCreate, FolderRead, FolderUpdate
from app.models.folderManager import FolderManager
from app.controllers.getProjectController import get_project_logic

import os
from pathlib import Path
import uuid
import re


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_FOLDER_PATH = SCRIPT_DIR.parent.parent /"storage"
"""
CREATE FOLDER LOGIC

"""
def _sanitize_name(name: str) -> str:
    # Keep only safe filename characters, replace others with underscore
    safe = re.sub(r'[^A-Za-z0-9._-]', '_', name)
    return safe[:255] if len(safe) > 255 else safe


def _unique_path(base: Path) -> Path:
    # If base exists, append a numeric suffix to make it unique
    if not base.exists():
        return base
    stem = base.stem
    parent = base.parent
    suffix = base.suffix
    counter = 1
    while True:
        candidate = parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def _create_filesystem_folder(
    folder_data: dict, 
    projectid: str
) -> Path:
    """
    Determines the unique folder path, creates the physical directory on disk,
    and returns the absolute Path object.
    """
    
    # Determine a safe folder name:
    raw_name = None
    # Common possible name fields - check them in order
    for key in ("name", "title", "folder_name", "dirname"):
        if key in folder_data and folder_data.get(key):
            raw_name = str(folder_data.get(key))
            break

    if not raw_name:
        # fallback to a generated name
        raw_name = f"folder_{uuid.uuid4().hex[:8]}"

    # 1. Sanitize name and define project path
    safe_name = _sanitize_name(Path(raw_name).name)
    project_dir = DEFAULT_FOLDER_PATH / str(projectid)
    target_folder = project_dir / safe_name
    
    # 2. Ensure uniqueness (don't overwrite existing folder)
    target_folder = _unique_path(target_folder)

    # 3. Create the folder on disk
    try:
        # parents=True creates the project_dir if it doesn't exist
        # exist_ok=False raises an error if the unique path was somehow not unique
        target_folder.mkdir(parents=True, exist_ok=False)
    except Exception as exc:
        # Raise HTTPException for upstream API handling
        raise HTTPException(status_code=500, detail=f"Unable to create folder on disk: {exc}")

    return target_folder

def create_folder_in_project(
    folder_data: FolderCreate,
    projectid: str,
    user_id: int,  # Add user_id parameter
    db: Session
) -> FolderRead:
    # 1. Validate project exists
    get_project_logic(projectid)

    # 2. Prepare folder metadata (exclude id AND userid)
    folder_dict = folder_data.model_dump(exclude={"id", "userid"})
    
    # 3. Create the folder on disk and get its final path
    target_folder = _create_filesystem_folder(folder_dict, projectid) 

    # 4. Save folder record in DB with userid
    db_folder = FolderDB(
        **folder_dict,
        userid=user_id  # Set the userid from authenticated user
    )
    
    # Set the path field on the DB model
    fs_path = str(target_folder.resolve())
    for attr in ("path", "directory", "dir", "location", "filepath"):
        if hasattr(db_folder, attr):
            try:
                setattr(db_folder, attr, fs_path)
            except Exception:
                pass

    db.add(db_folder)
    db.commit()
    db.refresh(db_folder)

    # 5. Link folder to project
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

"""
READ FOLDER LOGIC

"""
def get_folder_logic(folder_id: int, db: Session) -> FolderRead:
    stmt = select(FolderDB).where(FolderDB.id == folder_id)
    db_folder = db.exec(stmt).first()
    if not db_folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    return FolderRead.from_orm(db_folder)


def list_folders_logic(user_id: int, db: Session, skip: int = 0, limit: int = 100) -> list[FolderRead]:
    stmt = select(FolderDB).where(FolderDB.userid == user_id).offset(skip).limit(limit)
    folders = db.exec(stmt).all()
    return [FolderRead.from_orm(f) for f in folders]

"""
UPDATE FOLDER LOGIC

"""

def update_folder_in_project(
    folder_id: int,
    update_data: FolderUpdate,   # Pydantic model with optional fields: name, etc.
    projectid: str,
    db: Session
) -> FolderRead:
    # 1. Get the existing folder record (and verify it belongs to the project)
    db_folder = db.query(FolderDB).filter(
        FolderDB.id == folder_id
    ).join(FolderManager).filter(
        FolderManager.projectid == projectid
    ).first()

    if not db_folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    # Get current filesystem path from the attribute that holds it
    current_fs_path_str = None
    for attr in ("path", "directory", "dir", "location", "filepath"):
        if hasattr(db_folder, attr) and getattr(db_folder, attr):
            current_fs_path_str = getattr(db_folder, attr)
            break

    if not current_fs_path_str:
        raise HTTPException(status_code=500, detail="Folder path not stored in DB")

    current_path = Path(current_fs_path_str)

    if not current_path.exists():
        raise HTTPException(status_code=500, detail="Folder missing on filesystem")

    update_dict = update_data.model_dump(exclude_unset=True)  # only fields that were sent

    new_path = current_path

    # Only rename on disk if a new name/title is provided
    if any(key in update_dict for key in ("name", "title", "folder_name", "dirname")):
        raw_name = next(
            (update_dict[key] for key in ("name", "title", "folder_name", "dirname") if update_dict.get(key)),
            None
        )
        if raw_name:
            safe_name = _sanitize_name(Path(raw_name).name)
            proposed_path = current_path.parent / safe_name

            # Ensure uniqueness (same logic as creation)
            proposed_path = _unique_path(proposed_path)

            # Move folder on disk
            try:
                current_path.rename(proposed_path)
                new_path = proposed_path
            except Exception as exc:
                raise HTTPException(status_code=500, detail=f"Failed to rename folder on disk: {exc}")

    # Update other fields in DB (name, description, etc.)
    for key, value in update_dict.items():
        if hasattr(db_folder, key):
            setattr(db_folder, key, value)

    # Update the path field in DB
    new_fs_path_str = str(new_path.resolve())
    for attr in ("path", "directory", "dir", "location", "filepath"):
        if hasattr(db_folder, attr):
            setattr(db_folder, attr, new_fs_path_str)

    db.commit()
    db.refresh(db_folder)

    return FolderRead.from_orm(db_folder)

# def update_folder_logic(folder_id: int, folder_up: FolderUpdate, db: Session) -> FolderRead:
#     db_folder = db.get(FolderDB, folder_id)
#     if not db_folder:
#         raise HTTPException(status_code=404, detail="Folder not found")
    
#     data = folder_up.model_dump(exclude_unset=True)
#     for k, v in data.items():
#         setattr(db_folder, k, v)
    
#     db.add(db_folder)
#     db.commit()
#     db.refresh(db_folder)
#     return FolderRead.from_orm(db_folder)

"""
DELETE FOLDER LOGIC

NOTE: This implementation deletes the folder from both the database and the filesystem.
Be cautious with this operation, especially if folders may contain important data.
- Willing to move the folder to trash instead of permanent deletion if preferred. Then have a shedule to remove them later.
"""
def delete_folder_in_project(
    folder_id: int,
    projectid: str,
    db: Session
) -> dict:
    # 1. Get folder + verify ownership
    db_folder = db.query(FolderDB).filter(
        FolderDB.id == folder_id
    ).join(FolderManager).filter(
        FolderManager.projectid == projectid
    ).first()

    if not db_folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    # 2. Determine filesystem path
    fs_path_str = None
    for attr in ("path", "directory", "dir", "location", "filepath"):
        if hasattr(db_folder, attr) and getattr(db_folder, attr):
            fs_path_str = getattr(db_folder, attr)
            break

    folder_path = Path(fs_path_str) if fs_path_str else None

    # 3. Delete from filesystem (recursive, but careful!)
    if folder_path and folder_path.exists():
        try:
            import shutil
            shutil.rmtree(folder_path)  # removes folder + all contents
        except Exception as exc:
            # Log the error but continue – we still want to clean DB
            # (or you can raise if you prefer strict consistency)
            print(f"Warning: Failed to delete folder on disk {folder_path}: {exc}")

    # 4. Delete linking record first (or use cascade)
    db.query(FolderManager).filter(
        FolderManager.folderId == folder_id,
        FolderManager.projectid == projectid
    ).delete()

    # 5. Delete the folder record
    db.delete(db_folder)
    db.commit()

    return {"detail": "Folder deleted successfully"}


# def delete_folder_logic(folder_id: int, db: Session):
#     db_folder = db.get(FolderDB, folder_id)
#     if not db_folder:
#         raise HTTPException(status_code=404, detail="Folder not found")
#     db.delete(db_folder)
#     db.commit()