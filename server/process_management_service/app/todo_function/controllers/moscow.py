from sqlalchemy.orm import Session
from fastapi import HTTPException

# Models
from app.todo_function.models.element import  Element
from app.todo_function.models.todo import Todo
from app.todo_function.models.moscow import Moscow
from app.todo_function.models.task import Task
# Schemas
from app.todo_function.schemas import (
    TodoCreate, TodoUpdate, 
    MoscowCreate, MoscowUpdate, 
    TaskCreate, TaskUpdate
)

import uuid

def create_moscow(db: Session, moscow: MoscowCreate):
    """
    Creates a Moscow Board.
    """
    new_id = str(uuid.uuid4())
    db_moscow = Moscow(
        id=new_id,
        title=moscow.title,
        description=moscow.description,
        category=moscow.category
    )
    db.add(db_moscow)
    db.commit()
    db.refresh(db_moscow)
    return db_moscow

def get_moscows(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Moscow).offset(skip).limit(limit).all()

def get_moscow(db: Session, moscow_id: str):
    return db.query(Moscow).filter(Moscow.id == moscow_id).first()