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

def create_todo(db: Session, todo: TodoCreate):
    """
    Creates a Todo List.
    """
    new_id = str(uuid.uuid4())
    db_todo = Todo(
        id=new_id,
        title=todo.title,
        description=todo.description
        # 'type' is set automatically by SQLAlchemy polymorphic identity
    )
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def get_todos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Todo).offset(skip).limit(limit).all()

def get_todo(db: Session, todo_id: str):
    return db.query(Todo).filter(Todo.id == todo_id).first()