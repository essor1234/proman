from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.group import Group as GroupModel
from app.schemas.group import GroupCreate, UserGroupCreate, GroupUpdate
from app.core.group_client import GroupServiceClient 

# Initialize client
group_client = GroupServiceClient() 

# --- CREATE ---
def create_group(db: Session, group: GroupCreate, owner_id: int) -> dict:
    # 1. External Call
    external_group = group_client.create_group(
        name=group.name, 
        description=group.description, 
        owner_id=owner_id
    )

    # 2. Local Save (Reference)
    db_group = GroupModel(
        id=external_group['id'], 
        name=external_group['name']
    )
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    
    return external_group

# --- READ ---
def get_group(db: Session, group_id: int) -> dict:
    # 1. Fetch from external service
    external_group = group_client.get_group(group_id)
    
    if not external_group:
        return None
        
    # 2. Sync local name if needed (Self-healing cache)
    local_group = db.query(GroupModel).filter(GroupModel.id == group_id).first()
    if local_group and local_group.name != external_group['name']:
        local_group.name = external_group['name']
        db.commit()
        
    return external_group

def get_groups(db: Session, skip: int = 0, limit: int = 100) -> list[GroupModel]:
    return db.query(GroupModel).offset(skip).limit(limit).all()

# --- UPDATE (Added) ---
def update_group(db: Session, group_id: int, update: GroupUpdate, current_user_id: int) -> dict:
    """
    Updates group externally, then syncs local name.
    """
    # 1. Update Externally
    updated_external = group_client.update_group(
        group_id=group_id, 
        name=update.name, 
        user_id=current_user_id
    )

    # 2. Update Local Reference
    local_group = db.query(GroupModel).filter(GroupModel.id == group_id).first()
    if local_group:
        local_group.name = updated_external['name']
        db.commit()
        db.refresh(local_group)
        
    return updated_external

# --- DELETE (Added) ---
def delete_group(db: Session, group_id: int, current_user_id: int) -> dict:
    """
    Deletes group externally, then removes local reference.
    """
    # 1. Delete Externally
    group_client.delete_group(group_id, current_user_id)

    # 2. Delete Local Reference
    local_group = db.query(GroupModel).filter(GroupModel.id == group_id).first()
    if local_group:
        db.delete(local_group)
        db.commit()
        
    return local_group

# --- MEMBERSHIP (Delegated) ---
def add_member(db: Session, member_data: UserGroupCreate, added_by_user_id: int) -> dict:
    return group_client.add_group_member(
        group_id=member_data.groupId,
        user_id=member_data.userId,
        role=member_data.role,
        added_by_user_id=added_by_user_id
    )

def get_members(db: Session, group_id: int, current_user_id: int) -> list[dict]:
    return group_client.list_group_members(group_id, current_user_id)

def remove_member(db: Session, group_id: int, user_id: int) -> None:
    return group_client.remove_member(group_id, user_id)