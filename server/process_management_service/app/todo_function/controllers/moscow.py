from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.todo_function.models import Moscow
from app.todo_function.schemas import MoscowCreate

# ✅ NEW: Import the client
from app.todo_function.core.project_client import get_project_details

def create_moscow(db: Session, moscow: MoscowCreate):
    # 1. ✅ NEW: External Validation
    print(f"Verifying Project ID {moscow.project_id}...")
    project_data = get_project_details(moscow.project_id)
    
    if not project_data:
        raise HTTPException(
            status_code=404, 
            detail=f"Project ID {moscow.project_id} does not exist in Project Service."
        )

    # 2. Proceed with Creation
    db_moscow = Moscow(
        title=moscow.title,
        description=moscow.description,
        category=moscow.category,
        project_id=moscow.project_id
    )
    
    db.add(db_moscow)
    db.commit()
    db.refresh(db_moscow)
    return db_moscow

def get_moscows(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Moscow).offset(skip).limit(limit).all()

def get_moscow(db: Session, moscow_id: int):
    return db.query(Moscow).filter(Moscow.id == moscow_id).first()

def get_moscows_by_project(db: Session, project_id: int):
    return db.query(Moscow).filter(Moscow.project_id == project_id).all()