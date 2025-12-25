
"""
FastAPI routes for Group CRUD + member.
- Thin: only HTTP logic, delegates to repository.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.group import Group, GroupCreate, UserGroup, UserGroupCreate, GroupUpdate
from app.controllers.group import (
    create_group, add_member, get_groups, get_group, get_members,
    update_group, delete_group, remove_member
)

router = APIRouter(prefix="/groups", tags=["Groups"])

@router.post("/", response_model=Group, status_code=status.HTTP_201_CREATED)
def create(group: GroupCreate, db: Session = Depends(get_db)):
    return create_group(db, group)

@router.post("/members", response_model=UserGroup)
def add_user(member: UserGroupCreate, db: Session = Depends(get_db)):
    try:
        return add_member(db, member)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=list[Group])
def read_all(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_groups(db, skip, limit)

@router.get("/{group_id}", response_model=Group)
def read_one(group_id: int, db: Session = Depends(get_db)):
    group = get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group

@router.get("/{group_id}/members", response_model=list[UserGroup])
def read_members(group_id: int, db: Session = Depends(get_db)):
    group = get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return get_members(db, group_id)

@router.put("/{group_id}", response_model=Group)
def update(group_id: int, update: GroupUpdate, db: Session = Depends(get_db)):
    updated = update_group(db, group_id, update)
    if not updated:
        raise HTTPException(status_code=404, detail="Group not found")
    return updated

@router.delete("/{group_id}", response_model=Group)
def remove(group_id: int, db: Session = Depends(get_db)):
    deleted = delete_group(db, group_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Group not found")
    return deleted

@router.delete("/{group_id}/members/{user_id}", response_model=UserGroup)
def remove_user(group_id: int, user_id: int, db: Session = Depends(get_db)):
    deleted = remove_member(db, group_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="member not found")
    return deleted