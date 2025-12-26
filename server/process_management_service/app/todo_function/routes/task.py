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
    Task as TaskSchema, TaskCreate, TaskUpdate
)
from app.todo_function.controllers import (
    create_task, update_task, delete_element, delete_task)

# Controller Functions
# Importing directly from app.controllers thanks to __init__.py
from app.todo_function.controllers import (
    create_todo, get_todos, get_todo,
    create_moscow, get_moscows, get_moscow,
    create_task, update_task, delete_element
)

router = APIRouter(prefix="/process", tags=["Process Management"])

@router.post("/tasks/", response_model=TaskSchema, status_code=status.HTTP_201_CREATED)
def add_task(
    task: TaskCreate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Controller handles validation of parent ID
    return create_task(db, task)

@router.put("/tasks/{task_id}", response_model=TaskSchema)
def update_existing_task(
    task_id: int, 
    task_update: TaskUpdate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    updated = update_task(db, task_id, task_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated

@router.delete("/elements/{element_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_element(
    element_id: int, 
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

@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_task(
    task_id: int, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Deletes a single task.
    """
    deleted = delete_task(db, task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return None