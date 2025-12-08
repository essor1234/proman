from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Dependencies
from app.todo_function.core.database import get_db
from app.todo_function.core.security import get_current_user

# Schemas
# Importing directly from app.schemas thanks to __init__.py
# Note: aliases (TodoSchema, MoscowSchema) are already defined in __init__.py
from app.todo_function.schemas import (
    TodoSchema, TodoCreate,
    MoscowSchema, MoscowCreate,
    TaskSchema, TaskCreate, TaskUpdate
)

# Controller Functions
# Importing directly from app.controllers thanks to __init__.py
from app.todo_function.controllers import (
    create_todo, get_todos, get_todo,
    create_moscow, get_moscows, get_moscow,
    create_task, update_task, delete_element
)

router = APIRouter(prefix="/process", tags=["Process Management"])



@router.post("/todos/", response_model=TodoSchema, status_code=status.HTTP_201_CREATED)
def create_new_todo(
    todo: TodoCreate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return create_todo(db, todo)

@router.get("/todos/", response_model=List[TodoSchema])
def read_all_todos(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return get_todos(db, skip=skip, limit=limit)

@router.get("/todos/{todo_id}", response_model=TodoSchema)
def read_one_todo(
    todo_id: str, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    todo = get_todo(db, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@router.delete("/elements/{element_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_element(
    element_id: str, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Deletes a Todo list OR a Moscow board (and all their tasks).
    """
    deleted = delete_element(db, element_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Element not found")
    return None