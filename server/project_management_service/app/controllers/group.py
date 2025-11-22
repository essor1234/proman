"""
Repositories layer for Group operations.
- All SQLAlchemy queries for local data (Groups) are isolated here.
- Group Membership logic is entirely delegated to the external Group Service Client.
"""

from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.group import Group as GroupModel # GroupModel now uses UUIDs
from app.schemas.group import Group, GroupCreate, GroupUpdate, UserGroup, UserGroupCreate
from app.clients.account import get_account_user
from app.clients.group import GroupServiceClient 
from uuid import UUID

group_client = GroupServiceClient() # Initialize client

# CREATE
def create_group(db: Session, group: GroupCreate) -> GroupModel:
    """Creates a new group locally. The Group ID is locally generated (UUID)."""
    db_group = GroupModel(name=group.name)
    db.add(db_group)
    db.commit() 
    db.refresh(db_group)
    return db_group

def add_member(db: Session, group_id: UUID, user_id: int, role: str, added_by_user_id: int) -> dict:
    """
    DELEGATES membership addition to the external Group Management Service.
    """
    # 1. Validate external user ID (SSOT: Account Service)
    try:
        # Note: get_account_user needs to be updated to handle the integer user ID vs UUID context
        get_account_user(user_id) 
    except HTTPException as e:
        raise ValueError(f"Cannot add member: {e.detail}")

    # 2. Add member via Group Management Service (HTTP Call)
    try:
        membership_response = group_client.add_group_member(
            group_id=group_id, 
            user_id=user_id, 
            role=role, 
            added_by_user_id=added_by_user_id
        )
        return membership_response
    except HTTPException as e:
        raise ValueError(f"Group Service Error: {e.detail}")


# READ
def get_groups(db: Session, skip: int = 0, limit: int = 100) -> list[GroupModel]:
    """Retrieves local group entities."""
    return db.query(GroupModel).offset(skip).limit(limit).all()

def get_group(db: Session, group_id: UUID) -> GroupModel | None:
    """Retrieves a local group entity by UUID."""
    return db.query(GroupModel).filter(GroupModel.id == group_id).first()

def get_members(db: Session, group_id: UUID, current_user_id: int, status_filter: str | None) -> list[dict]:
    """
    DELEGATES listing members to the external Group Management Service.
    
    The user ID is required by the external service for authorization checks.
    """
    try:
        # 1. Check if the group exists locally first (for integrity)
        if not get_group(db, group_id):
            raise ValueError(f"Group ID {group_id} not found locally.")

        # 2. Call the external Group Service
        members_list = group_client.list_group_members(
            group_id=group_id, 
            current_user_id=current_user_id, 
            status_filter=status_filter
        )
        return members_list
    except HTTPException as e:
        raise ValueError(f"Group Service Error during member retrieval: {e.detail}")
    except ValueError as e:
        # Re-raise local errors
        raise e


# UPDATE
def update_group(db: Session, group_id: UUID, update: GroupUpdate) -> GroupModel | None:
    """Updates a local group entity."""
    db_group = get_group(db, group_id)
    if not db_group:
        return None
    if update.name is not None:
        db_group.name = update.name
    
    db.commit()
    db.refresh(db_group)
    return db_group

# DELETE
def delete_group(db: Session, group_id: UUID) -> GroupModel | None:
    """Deletes a local group entity."""
    db_group = get_group(db, group_id)
    if db_group:
        db.delete(db_group)
        db.commit()
    return db_group

# FIX: Reintroducing remove_member as a wrapper for the external service
def remove_member(db: Session, group_id: UUID, user_id: int, removed_by_user_id: int) -> None:
    """
    DELEGATES removal of a member to the external Group Management Service.
    """
    try:
        # 1. Check if the group exists locally first (for integrity)
        if not get_group(db, group_id):
            raise ValueError(f"Group ID {group_id} not found locally.")

        # 2. Call the external Group Service DELETE endpoint
        # The client's _make_request handles the actual HTTP DELETE call
        group_client._make_request(
            method="DELETE", 
            path=f"/{group_id}/members/{user_id}",
        )
        # Success (204 No Content) is handled in the client and returns None
        return None
    except HTTPException as e:
        raise ValueError(f"Group Service Error during member removal: {e.detail}")
    except ValueError as e:
        # Re-raise local errors
        raise e