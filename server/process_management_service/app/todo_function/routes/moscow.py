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

@router.post("/moscows/", response_model=MoscowSchema, status_code=status.HTTP_201_CREATED)
def create_new_moscow(
    moscow: MoscowCreate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return create_moscow(db, moscow)

@router.get("/moscows/", response_model=List[MoscowSchema])
def read_all_moscows(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return get_moscows(db, skip=skip, limit=limit)

@router.get("/moscows/{moscow_id}", response_model=MoscowSchema)
def read_one_moscow(
    moscow_id: str, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    moscow = get_moscow(db, moscow_id)
    if not moscow:
        raise HTTPException(status_code=404, detail="Moscow board not found")
    return moscow

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