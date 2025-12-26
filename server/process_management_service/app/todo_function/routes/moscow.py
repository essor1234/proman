from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.todo_function.core.database import get_db
from app.todo_function.core.security import get_current_user

# ✅ FIX: Import the real class names and ALIAS them here
from app.todo_function.schemas import (
    Moscow as MoscowSchema, MoscowCreate, MoscowUpdate,
    Todo as TodoSchema,     TodoCreate,
    Task as TaskSchema,     TaskCreate,   TaskUpdate
)

from app.todo_function.controllers import (
    create_moscow, 
    get_moscows, 
    get_moscow, 
    get_moscows_by_project, 
    update_moscow,
    delete_element  # <--- Add this here!
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
    moscow_id: int, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    moscow = get_moscow(db, moscow_id)
    if not moscow:
        raise HTTPException(status_code=404, detail="Moscow board not found")
    return moscow

@router.put("/{moscow_id}", response_model=MoscowSchema)
def update_existing_moscow(
    moscow_id: int,
    moscow_update: MoscowUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    updated = update_moscow(db, moscow_id, moscow_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Moscow board not found")
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