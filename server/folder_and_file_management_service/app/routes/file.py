# app/routes/file.py
from http.client import HTTPException
from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.core.database import get_db
from app.controllers.file import (
    create_file_logic,
    get_file_logic,
    list_files_logic,
    update_file_logic,
    delete_file_logic,
    get_files_by_user_logic,
)
from app.schemas.file import FileCreate, FileRead, FileUpdate
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.controllers.file import create_file_logic_with_userid
router = APIRouter(prefix="/files", tags=["files"])


# @router.post("/", response_model=FileRead, status_code=status.HTTP_201_CREATED)
# def create_file(file_in: FileCreate, db=Depends(get_db)):
#     return create_file_logic(file_in, db)
security = HTTPBearer()  # Accepts `Authorization: Bearer <token>`

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    # TODO: Replace with real JWT decode
    # For testing: accept any token that is a number
    try:
        user_id = int(token)
        return user_id
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/", response_model=FileRead, status_code=status.HTTP_201_CREATED)
def create_file(
    file_in: FileCreate,
    user_id: int = Depends(get_current_user_id),   # ← Automatically extracted
    db: Session = Depends(get_db)
):
    return create_file_logic_with_userid(file_in, user_id, db)

@router.get("/{file_id}", response_model=FileRead)
def read_file(file_id: int, db=Depends(get_db)):
    return get_file_logic(file_id, db)

@router.get("/user/{user_id}", response_model=list[FileRead])
def read_files_by_user(user_id: int, db=Depends(get_db)):
    return get_files_by_user_logic(user_id, db)







@router.get("/", response_model=list[FileRead])
def list_files(skip: int = 0, limit: int = 100, db=Depends(get_db)):
    return list_files_logic(db, skip, limit)


@router.patch("/{file_id}", response_model=FileRead)
def update_file(file_id: int, file_up: FileUpdate, db=Depends(get_db)):
    return update_file_logic(file_id, file_up, db)


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(file_id: int, db=Depends(get_db)):
    delete_file_logic(file_id, db)
    return None