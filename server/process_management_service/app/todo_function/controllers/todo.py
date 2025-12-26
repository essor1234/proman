from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.todo_function.models import Todo
from app.todo_function.schemas import TodoCreate, TodoUpdate
from app.todo_function.schemas import TodoUpdate

# ✅ NEW: Import the client
from app.todo_function.core.project_client import get_project_details

def create_todo(db: Session, todo: TodoCreate):
    # 1. ✅ NEW: External Validation
    print(f"Verifying Project ID {todo.project_id}...")
    project_data = get_project_details(todo.project_id)
    
    if not project_data:
        raise HTTPException(
            status_code=404, 
            detail=f"Project ID {todo.project_id} does not exist in Project Service."
        )

    # 2. Proceed with Creation
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        project_id=todo.project_id
    )
    
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def get_todos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Todo).offset(skip).limit(limit).all()

def get_todo(db: Session, todo_id: int):
    return db.query(Todo).filter(Todo.id == todo_id).first()

def get_todos_by_project(db: Session, project_id: int):
    return db.query(Todo).filter(Todo.project_id == project_id).all()

def update_todo(db: Session, todo_id: int, todo_data: TodoUpdate):
    """
    Updates the title or description of a Todo list.
    """
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not db_todo:
        return None
    
    if todo_data.title is not None:
        db_todo.title = todo_data.title
    
    if todo_data.description is not None:
        db_todo.description = todo_data.description

    db.commit()
    db.refresh(db_todo)
    return db_todo