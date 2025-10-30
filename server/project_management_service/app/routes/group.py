# In routes/group.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import (
    get_db, 
    Group as GroupModel, 
    User as UserModel, 
    UserGroup as UserGroupModel
)
from schemas.group import Group, GroupCreate, UserGroup, UserGroupCreate, GroupUpdate

router = APIRouter(
    prefix="/groups",
    tags=["Groups"]
)

# POST ENDPOINT (CREATE)
@router.post("/", response_model=Group)
def create_group(group: GroupCreate, db: Session = Depends(get_db)):
    db_group = GroupModel(name=group.name)
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

@router.post("/users", response_model=UserGroup)
def add_user_in_group(user_group: UserGroupCreate, db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(UserModel).filter(UserModel.id == user_group.userId).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {user_group.userId} not found")
    
    # Check if group exists
    group = db.query(GroupModel).filter(GroupModel.id == user_group.groupId).first()
    if not group:
        raise HTTPException(status_code=404, detail=f"Group with id {user_group.groupId} not found")

    # Check if this relationship already exists
    db_user_group_check = db.query(UserGroupModel).filter(
        UserGroupModel.userId == user_group.userId,
        UserGroupModel.groupId == user_group.groupId
    ).first()
    
    if db_user_group_check:
        raise HTTPException(status_code=400, detail="User is already in this group")
    
    # Create the new association
    db_user_group = UserGroupModel(
        userId=user_group.userId,
        groupId=user_group.groupId,
        role=user_group.role
    )
    db.add(db_user_group)
    db.commit()
    db.refresh(db_user_group)
    return db_user_group

# GET ENDPOINT (READ)
@router.get("/", response_model=list[Group])
def read_groups(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    groups = db.query(GroupModel).offset(skip).limit(limit).all()
    return groups

@router.get("/{group_id}", response_model=Group)
def read_group(group_id: int, db: Session = Depends(get_db)):
    group = db.query(GroupModel).filter(GroupModel.id == group_id).first()
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    return group

# PUT ENDPOINT (UPDATE)
@router.put("/",response_model=Group)
def update_group(group_id: int, group: GroupUpdate ,db: Session = Depends(get_db)):
    db_group = db.query(GroupModel).filter(GroupModel.id == group_id).first()
    if db_group is None:
         raise HTTPException(status_code=404, detail="Group not found")
    
    db_group.name=group.name if group.name is not None else db_group.name
    
    db.commit()
    db.refresh(db_group)
    return db_group

#DELETE ENDPOINT (DELETE)
@router.delete("/{group_id}", response_model=Group)
def delete_group(group_id: int, db: Session = Depends(get_db)):
    db_group = db.query(GroupModel).filter(GroupModel.id == group_id).first()
    if db_group is None:
         raise HTTPException(status_code=404, detail="Group not found")
    
    db.delete(db_group)
    db.commit()
    return db_group