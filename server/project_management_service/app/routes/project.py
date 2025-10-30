# In routes/project.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import(
    get_db, 
    Project as ProjectModel, 
    User as UserModel, 
    ProjectMember as ProjectMemberModel
)
from schemas.project import Project, ProjectCreate, ProjectMember, ProjectMemberCreate, ProjectUpdate

router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)

# POST ENDPOINT (CREATE)
@router.post("/", response_model=Project)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    db_project = ProjectModel(name=project.name)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.post("/members", response_model=ProjectMember)
def add_member_to_project(project_member:ProjectMemberCreate, db:Session = Depends(get_db)):
     # Check if user exists
    user = db.query(UserModel).filter(UserModel.id == project_member.userId).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {project_member.userId} not found")
    
    # Check if group exists
    project = db.query(ProjectModel).filter(ProjectModel.id == project_member.projectId).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project with id {project_member.projectId} not found")
    # Check if this relationship already exists
    db_project_member_check = db.query(ProjectMemberModel).filter(
        ProjectMemberModel.userId == project_member.userId,
        ProjectMemberModel.projectId == project_member.projectId
    ).first()
    
    if db_project_member_check:
        raise HTTPException(status_code=400, detail="User is already in this group")
    
    # Create the new association
    db_project_member = ProjectMemberModel(
        userId=project_member.userId,
        projectId=project_member.projectId,
        role=project_member.role
    )
    db.add(db_project_member)
    db.commit()
    db.refresh(db_project_member)
    return db_project_member


# GET ENDPOINT (READ)
@router.get("/", response_model=list[Project])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    projects = db.query(ProjectModel).offset(skip).limit(limit).all()
    return projects

@router.get("/{project_id}", response_model=Project)
def read_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

#POST ENDPOINT (UPDATE)
@router.put("/{project_id}", response_model=Project)
def update_project(project_id:int, project: ProjectUpdate, db:Session = Depends(get_db)):
    db_project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db_project.name=project.name if project.name is not None else db_project.name
    db_project.groupId=project.groupId if project.groupId is not None else db_project.groupId


    db.commit()
    db.refresh(db_project)
    return db_project

#DELETE ENDPOINT (DELETE)
@router.delete("/{project_id}", response_model=Project)
def delete_group(project_id: int, db: Session = Depends(get_db)):
    db_project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if db_project is None:
         raise HTTPException(status_code=404, detail="Group not found")
    
    db.delete(db_project)
    db.commit()
    return db_project