# project_service/app/repositories/group.py
"""
Repository layer for Group & UserGroup (member) operations.
- All SQLAlchemy queries are isolated here.
- Routes only call these functions.
"""

from sqlalchemy.orm import Session
from app.models.group import Group as GroupModel, UserGroup as UserGroupModel
from app.schemas.group import Group, GroupCreate, GroupUpdate, UserGroup, UserGroupCreate

#CREATE
def create_group(db:Session, group:GroupCreate):
    db_group = GroupModel(name=group.name)
    db.add(db_group)
    db.commit
    db.refresh(db_group)
    return db_group

def add_member(db:Session, member:UserGroupCreate):
    # Validate user exists
    user = db.query(db.model.User).filter(db.model.User.id == member.userId).first()
    if not user:
        raise ValueError(f"User with id {member.userId} not found")

    # Validate group exists
    group = db.query(GroupModel).filter(GroupModel.id == member.groupId).first()
    if not group:
        raise ValueError(f"Group with id {member.groupId} not found")

    # Prevent duplicates
    exists = db.query(UserGroupModel).filter(
        UserGroupModel.userId == member.userId,
        UserGroupModel.groupId == member.groupId
    ).first()
    if exists:
        raise ValueError("User is already in this group")

    # Insert
    db_member = UserGroupModel(
        userId=member.userId,
        groupId=member.groupId,
        role=member.role
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
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