from sqlalchemy.orm import Session
from app.todo_function.models import Moscow
from app.todo_function.schemas import MoscowCreate

def create_moscow(db: Session, moscow: MoscowCreate):
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

# ✅ RESTORE THIS FUNCTION
def get_moscows(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Moscow).offset(skip).limit(limit).all()

def get_moscow(db: Session, moscow_id: int):
    return db.query(Moscow).filter(Moscow.id == moscow_id).first()

def get_moscows_by_project(db: Session, project_id: int):
    return db.query(Moscow).filter(Moscow.project_id == project_id).all()