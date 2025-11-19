"""
Repositories layer for Group & UserGroup (member) operations.
- All SQLAlchemy queries are isolated here.
- Routes only call these functions.
"""

from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.group import Group as GroupModel, UserGroup as UserGroupModel
from app.schemas.group import Group, GroupCreate, GroupUpdate, UserGroup, UserGroupCreate
from app.client.account import get_account_user

# CREATE
def create_group(db: Session, group: GroupCreate):
    """Creates a new group in the database."""
    db_group = GroupModel(name=group.name)
    db.add(db_group)
    
    # 🐛 FIX: Must CALL the commit function with parentheses 
    db.commit() 
    
    db.refresh(db_group)
    return db_group

def add_member(db: Session, member: UserGroupCreate) -> UserGroup:
    """Adds a user as a member to a group after validating the user ID."""
    # 1. VALIDATE USER ID AGAINST ACCOUNT SERVICE (New Step!)
    try:
        # This will raise a 404/503 HTTPException if the user is invalid/service is down
        get_account_user(member.userId) 
    except HTTPException as e:
        # Re-raise the exception with context/detail
        raise ValueError(e.detail) # Raising ValueError to be caught by the router's try/except

    # TODO: Add logic here to check if the group exists (get_group(db, member.groupId))
    # TODO: Add logic here to check for existing membership 

    # 4. If all checks pass, create the local link
    # 🐛 FIX: Using the imported ORM Model (UserGroupModel), not the Pydantic Schema (UserGroup)
    db_member = UserGroupModel(
        userId=member.userId, 
        groupId=member.groupId, 
        role=member.role
    )
    
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    
    # Return the Pydantic schema model (UserGroup) for the API response
    return db_member

# READ
def get_groups(db: Session, skip: int = 0, limit: int = 100):
    return db.query(GroupModel).offset(skip).limit(limit).all()

def get_group(db: Session, group_id: int):
    return db.query(GroupModel).filter(GroupModel.id == group_id).first()

def get_members(db: Session, group_id: int):
    return db.query(UserGroupModel).filter(UserGroupModel.groupId == group_id).all()

# UPDATE
def update_group(db: Session, group_id: int, update: GroupUpdate):
    db_group = get_group(db, group_id)
    if not db_group:
        return None
    if update.name is not None:
        db_group.name = update.name
    db.commit()
    db.refresh(db_group)
    return db_group

# DELETE
def delete_group(db: Session, group_id: int):
    # Retrieve the object before deleting
    db_group = get_group(db, group_id)
    if db_group:
        db.delete(db_group)
        db.commit()
    return db_group

def remove_member(db: Session, group_id: int, user_id: int):
    member = db.query(UserGroupModel).filter(
        UserGroupModel.groupId == group_id,
        UserGroupModel.userId == user_id
    ).first()
    if member:
        db.delete(member)
        db.commit()
    return member