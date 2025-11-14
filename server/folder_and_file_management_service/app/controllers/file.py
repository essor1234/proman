from http.client import HTTPException
from fastapi.params import Depends
from sqlmodel import SQLModel, Field, Session, select

from app.schemas.file import FileCreate, FileRead, FileUpdate, FileDelete
from app.models.file import FileDB
from app.controllers.getAccountController import get_account_user_logic
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


"""
TODO: Add get_account_user_logic to create_file_logic to verify user existence before file creation.
"""

security = HTTPBearer()  # Accepts `Authorization: Bearer <token>`


def create_file_logic_with_userid(file_in: FileCreate, current_user_id: int, db: Session) -> FileRead:
    # Validate user exists in Account Service
    get_account_user_logic(current_user_id)

    # EXCLUDE userid from input (even if client sent it)
    data = file_in.model_dump(exclude={"userid"})  # ← THIS IS KEY

    db_file = FileDB(
        **data,
        userid=current_user_id  # ← ONLY source of truth
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return FileRead.from_orm(db_file)

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    # TODO: Replace with real JWT decode
    # For testing: accept any token that is a number
    try:
        user_id = int(token)
        return user_id
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

def create_file_logic(file_in: FileCreate, db: Session) -> FileRead:
    db_file = FileDB(**file_in.model_dump())
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return FileRead.from_orm(db_file)


def get_file_logic(file_id: int, db: Session) -> FileRead:
    db_file = db.get(FileDB, file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    return FileRead.from_orm(db_file)


def list_files_logic(db: Session, skip: int = 0, limit: int = 100) -> list[FileRead]:
    stmt = select(FileDB).offset(skip).limit(limit)
    files = db.exec(stmt).all()
    return [FileRead.from_orm(f) for f in files]

def get_files_by_user_logic(user_id: int, db: Session) -> list[FileRead]:
    stmt = select(FileDB).where(FileDB.userid == user_id)
    files = db.exec(stmt).all()
    return [FileRead.from_orm(f) for f in files]

def update_file_logic(file_id: int, file_up: FileUpdate, db: Session) -> FileRead:
    db_file = db.get(FileDB, file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    data = file_up.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(db_file, k, v)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return FileRead.from_orm(db_file)


def delete_file_logic(file_id: int, db: Session):
    db_file = db.get(FileDB, file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    db.delete(db_file)
    db.commit()

