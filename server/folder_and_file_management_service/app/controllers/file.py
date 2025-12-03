from ast import Dict
from http.client import HTTPException
from typing import Any
from fastapi.params import Depends
from sqlmodel import SQLModel, Field, Session, select

from app.schemas.file import FileCreate, FileRead, FileUpdate, FileDelete
from app.models.file import FileDB
from app.controllers.getAccountController import get_account_user_logic
from app.controllers.getProjectController import get_project_logic

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException 

from pathlib import Path
import uuid
import re

"""
TODO: Create file on a specific project
"""
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_FILE_PATH = SCRIPT_DIR.parent.parent / "storage" 

security = HTTPBearer()  # Accepts `Authorization: Bearer <token>`
"""
CREATE FILE LOGIC

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
    suffix = base.suffix # Crucial for files: keeps the extension
    counter = 1
    
    while True:
        # Append counter before the suffix (extension)
        candidate = parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1
        
def _create_filesystem_file(
    file_data: dict[str, Any], 
    projectid: int
) -> Path:
    """
    Determines the unique file path, creates the physical file on disk,
    writes the content, and returns the absolute Path object.
    """
    
    # 1. Determine a safe file name
    raw_name = file_data.get("name")
    
    # Get content. If key is missing OR value is None, default to empty string.
    content = file_data.get("content")
    if content is None:
        content = ""

    if not raw_name:
        raw_name = f"file_{uuid.uuid4().hex[:8]}.txt" 

    # 2. Sanitize name and define project path
    safe_name = _sanitize_name(Path(raw_name).name) 
    project_dir = DEFAULT_FILE_PATH / str(projectid)
    target_file = project_dir / safe_name
    
    # 3. Ensure uniqueness (don't overwrite existing file)
    target_file = _unique_path(target_file)

    # 4. Create parent directory if it doesn't exist
    try:
        project_dir.mkdir(parents=True, exist_ok=True)
    except Exception as exc:
        # This will now work correctly with FastAPI's exception
        raise HTTPException(status_code=500, detail=f"Unable to create project directory on disk: {exc}")

    # 5. Write content to the file
    try:
        # Determine mode: 'wb' for bytes, 'w' for string
        mode = 'wb' if isinstance(content, bytes) else 'w'
        
        # If content is string, specify encoding to avoid issues
        encoding = 'utf-8' if mode == 'w' else None
        
        with open(target_file, mode, encoding=encoding) as f:
            f.write(content)
            
    except Exception as exc:
        # This will now work correctly with FastAPI's exception
        raise HTTPException(status_code=500, detail=f"Unable to write file content to disk: {exc}")

    return target_file

def create_file_logic_with_userid(file_in: FileCreate, 
                                  current_user_id: int, 
                                  db: Session,
                                  projectid: int) -> FileRead:
    # Validate user exists in Account Service
    get_account_user_logic(current_user_id)
    get_project_logic(projectid)

    # EXCLUDE userid from input (even if client sent it)
    data = file_in.model_dump(exclude={"userid", "id", "path", "size", "date_created"})

    full_data = file_in.model_dump(exclude={"userid"})
    target_file_path = _create_filesystem_file(full_data, projectid) 

    # If size wasn't provided, calculate it from the created file
    if data.get('size') is None:
        import os
        if target_file_path.exists():
            data['size'] = os.path.getsize(target_file_path)
        else:
            # Fallback if file doesn't exist yet
            data['size'] = 0


    # Save file record in DB
    db_file = FileDB(
        **data,
        userid=current_user_id, # ONLY source of truth
        path=str(target_file_path.resolve())
    )
    
    # Set the path field on the DB model
    fs_path = str(target_file_path.resolve())

    # Assuming 'path' is the column name on FileDB
    if hasattr(db_file, "path"):
        db_file.path = fs_path
    elif hasattr(db_file, "filepath"):
        db_file.filepath = fs_path


    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return FileRead.from_orm(db_file)

def create_file_logic(file_in: FileCreate, db: Session) -> FileRead:
    db_file = FileDB(**file_in.model_dump())
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return FileRead.from_orm(db_file)

"""
READ FILE LOGIC

"""
def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    # TODO: Replace with real JWT decode
    # For testing: accept any token that is a number
    try:
        user_id = int(token)
        return user_id
    except:
        raise HTTPException(status_code=401, detail="Invalid token")



def get_file_logic(file_id: int, db: Session) -> FileRead:
    db_file = db.get(FileDB, file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    return FileRead.from_orm(db_file)

def list_files_logic(user_id: int, db: Session, skip: int = 0, limit: int = 100) -> list[FileRead]:
    stmt = select(FileDB).where(FileDB.userid == user_id).offset(skip).limit(limit)
    files = db.exec(stmt).all()
    return [FileRead.from_orm(f) for f in files]

# def list_files_logic(db: Session, skip: int = 0, limit: int = 100) -> list[FileRead]:
#     stmt = select(FileDB).offset(skip).limit(limit)
#     files = db.exec(stmt).all()
#     return [FileRead.from_orm(f) for f in files]

def get_files_by_user_logic(user_id: int, db: Session) -> list[FileRead]:
    stmt = select(FileDB).where(FileDB.userid == user_id)
    files = db.exec(stmt).all()
    return [FileRead.from_orm(f) for f in files]
"""
UPDATE FILE LOGIC

"""

def update_file_logic(
    file_id: int,
    file_up: FileUpdate,
    db: Session
) -> FileRead:
    """
    Update file metadata AND/OR content AND/OR rename (move on disk).
    Fully synchronized with filesystem.
    """
    db_file = db.get(FileDB, file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    # Get current filesystem path from DB
    current_path_str = getattr(db_file, "path", None) or getattr(db_file, "filepath", None)
    if not current_path_str:
        raise HTTPException(status_code=500, detail="File path not stored in database")
    
    current_path = Path(current_path_str)
    if not current_path.exists():
        raise HTTPException(status_code=500, detail="File missing on disk")

    update_data = file_up.model_dump(exclude_unset=True)
    new_path = current_path

    # === 1. Handle rename (name change) → move file on disk ===
    new_name = None
    for key in ("name", "filename", "title"):
        if update_data.get(key):
            new_name = update_data[key]
            break

    if new_name and new_name != current_path.name:
        safe_name = _sanitize_name(Path(new_name).name)
        proposed_path = current_path.parent / safe_name
        proposed_path = _unique_path(proposed_path)  # avoid collisions

        try:
            current_path.rename(proposed_path)
            new_path = proposed_path
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Failed to rename file on disk: {exc}")

    # === 2. Handle content update ===
    if "content" in update_data:
        content = update_data["content"]
        if content is None:
            content = ""  # allow clearing file

        mode = 'wb' if isinstance(content, bytes) else 'w'
        encoding = 'utf-8' if mode == 'w' else None

        try:
            with open(new_path, mode, encoding=encoding) as f:
                f.write(content)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Failed to write new content to file: {exc}")

    # === 3. Update DB fields (including new path) ===
    for key, value in update_data.items():
        if hasattr(db_file, key):
            setattr(db_file, key, value)

    # Always update the stored path in case of rename
    final_path_str = str(new_path.resolve())
    if hasattr(db_file, "path"):
        db_file.path = final_path_str
    elif hasattr(db_file, "filepath"):
        db_file.filepath = final_path_str

    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    return FileRead.from_orm(db_file)

# def update_file_logic(file_id: int, file_up: FileUpdate, db: Session) -> FileRead:
#     db_file = db.get(FileDB, file_id)
#     if not db_file:
#         raise HTTPException(status_code=404, detail="File not found")
#     data = file_up.model_dump(exclude_unset=True)
#     for k, v in data.items():
#         setattr(db_file, k, v)
#     db.add(db_file)
#     db.commit()
#     db.refresh(db_file)
#     return FileRead.from_orm(db_file)
"""
DELETE FILE LOGIC

"""
def delete_file_logic(file_id: int, db: Session) -> dict:
    """
    Delete file from database AND filesystem.
    Safe even if file is already missing.
    """
    db_file = db.get(FileDB, file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    # Get path from DB
    fs_path_str = getattr(db_file, "path", None) or getattr(db_file, "filepath", None)
    file_path = Path(fs_path_str) if fs_path_str else None

    # Remove from filesystem
    if file_path and file_path.exists():
        try:
            file_path.unlink()  # deletes the file
            # Optional: remove empty parent dirs? Usually not needed
        except Exception as exc:
            print(f"Warning: Could not delete file from disk {file_path}: {exc}")
            # You can choose to raise here if you want strict consistency

    # Remove from database
    db.delete(db_file)
    db.commit()

    return {"detail": "File deleted successfully"}

# def delete_file_logic(file_id: int, db: Session):
#     db_file = db.get(FileDB, file_id)
#     if not db_file:
#         raise HTTPException(status_code=404, detail="File not found")
#     db.delete(db_file)
#     db.commit()

