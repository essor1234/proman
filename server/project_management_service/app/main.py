from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel, ConfigDict, EmailStr
from db.database import (
    User as UserModel, 
    Group as GroupModel,
    Project as ProjectModel,
    UserGroup as UserGroupModel,
    ProjectMember as ProjectMemberModel,
    sessionLocal,
    engine, 
    Base    
)
from schemas.project import *
from sqlalchemy.orm import Session 

app = FastAPI(
    title="Project management service",
    description="Manage your own project",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    # allow_origins= settings.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)

# This line tells SQLAlchemy to create all tables defined in database.py
# (which inherit from Base) if they don't already exist.
Base.metadata.create_all(bind=engine)

# DATABASE DEPENDENCY


def get_db():
    db=sessionLocal()
    try:
        yield db
    finally:
        db.close()


# API ENDPOINTS
#POST ENDPOINT (CREATE)
@app.post("/users/", response_model=User)

def create_user(user: UserCreate, db: Session = Depends(get_db)):
    
    db_user = UserModel(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user # FastAPI will convert this to the 'User' Pydantic response_model

@app.post("/groups/", response_model=Group)

def create_group(group: GroupCreate, db: Session = Depends(get_db)):
    db_group = GroupModel(name=group.name)
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

@app.post("/projects/", response_model=Project)

def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    db_project = ProjectModel(name=project.name)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.post("/groups/users", response_model=UserGroup)

def add_user_in_group(user_group:UserGroupCreate,db: Session = Depends(get_db)):
    
    # Check if user exists
    user = db.query(UserModel).filter(UserModel.id == user_group.userId).first()
    if not user:
        raise HTTPException(status_code=404,detail=f"User with id {user_group.userId} not found")
    
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

@app.post("/projects/members")


#GET ENDPOINT (READ)
#GET USERS
@app.get("/users/", response_model=list[User])
def read_users(skip:int = 0, limit: int = 100, db:Session = Depends(get_db)):
    users = db.query(UserModel).offset(skip).limit(limit).all()
    return users

@app.get("/users/{user_id}", response_model=User)
def read_user(user_id: int, db:Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

#GET GROUPS
@app.get("/groups/", response_model=list[Group])
def read_groups(skip:int = 0, limit: int = 100, db:Session = Depends(get_db)):
    groups = db.query(GroupModel).offset(skip).limit(limit).all()
    return groups

@app.get("/groups/{group_id}", response_model=Group)
def read_group(group_id: int, db:Session = Depends(get_db)):
    group = db.query(GroupModel).filter(GroupModel.id == group_id).first()

    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    return group

#GET PROJECTS
@app.get("/projects/", response_model=list[Project])
def read_projects(skip:int = 0, limit: int = 100, db:Session = Depends(get_db)):
    projects = db.query(ProjectModel).offset(skip).limit(limit).all()
    return projects

@app.get("/projects/{project_id}", response_model=Project)
def read_project(project_id: int, db:Session = Depends(get_db)):
    project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project



if __name__ == "__main__":
    uvicorn.run("main:app", host = "0.0.0.0", port=8000, reload=True)

