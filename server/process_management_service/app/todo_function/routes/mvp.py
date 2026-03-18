from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.todo_function.core.database import get_db
from app.todo_function.core.security import get_current_user
from app.todo_function.schemas import MVP as MVPSchema, MVPCreate, MVPUpdate
from app.todo_function.controllers import (
    create_mvp, get_mvps, get_mvp, get_mvps_by_element, update_mvp, delete_mvp
)

router = APIRouter(prefix="/process", tags=["MVP"])

@router.post("/mvps/", response_model=MVPSchema, status_code=status.HTTP_201_CREATED)
def create_new_mvp(
    mvp: MVPCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new MVP item attached to an element"""
    return create_mvp(db, mvp)

@router.get("/mvps/", response_model=List[MVPSchema])
def read_all_mvps(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all MVP items with pagination"""
    return get_mvps(db, skip=skip, limit=limit)

@router.get("/mvps/{mvp_id}", response_model=MVPSchema)
def read_one_mvp(
    mvp_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a single MVP item by ID"""
    mvp = get_mvp(db, mvp_id)
    if not mvp:
        raise HTTPException(status_code=404, detail="MVP not found")
    return mvp

@router.get("/elements/{element_id}/mvps/", response_model=List[MVPSchema])
def read_mvps_by_element(
    element_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all MVP items for a specific element"""
    return get_mvps_by_element(db, element_id)

@router.put("/mvps/{mvp_id}", response_model=MVPSchema)
def update_existing_mvp(
    mvp_id: int,
    mvp_update: MVPUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update an MVP item"""
    updated = update_mvp(db, mvp_id, mvp_update)
    if not updated:
        raise HTTPException(status_code=404, detail="MVP not found")
    return updated

@router.delete("/mvps/{mvp_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_mvp(
    mvp_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete an MVP item"""
    deleted = delete_mvp(db, mvp_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="MVP not found")