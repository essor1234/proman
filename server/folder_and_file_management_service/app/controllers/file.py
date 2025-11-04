from http.client import HTTPException
from sqlmodel import SQLModel, Field, Session, select

from app.schemas.file import FileCreate, FileRead, FileUpdate, FileDelete
from app.models.file import FileDB


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

