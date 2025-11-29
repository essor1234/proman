from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.schemas.project import Project, ProjectCreate, ProjectMember, ProjectMemberCreate, ProjectUpdate
from app.controllers.project import (
    create_project, add_member, get_projects, get_project, get_members,
    update_project, delete_project, remove_member
)
# Import authentication dependency
from app.core.security import get_current_user

router = APIRouter(prefix="/projects", tags=["Projects"])

# app/routes/project.py

@router.post("/", response_model=Project, status_code=status.HTTP_201_CREATED)
def create(
    project: ProjectCreate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    authorization: Optional[str] = Header(None) 
):
    # --- CHANGED: Handle missing token safely ---
    if authorization:
        token = authorization.split(" ")[1] 
    else:
        # Send a dummy string so the function doesn't crash.
        # Since we are disabling security on the Group Service too (Step 3), this value doesn't matter.
        token = "temp_bypass_token" 
    # --------------------------------------------

    return create_project(
        db=db, 
        project=project, 
        owner_id=int(current_user["id"]), 
        token=token
    )
@router.post("/members", response_model=ProjectMember)
def add_user(project_member: ProjectMemberCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        # Pass current_user["id"] as the person adding the member
        return add_member(db, project_member, added_by_id=int(current_user["id"]))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=list[Project])
def read_all(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_projects(db, skip, limit)

@router.get("/{project_id}", response_model=Project)
def read_one(project_id: int, db: Session = Depends(get_db)):
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.get("/{project_id}/members", response_model=list[ProjectMember])
def read_members(project_id: int, db: Session = Depends(get_db)):
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return get_members(db, project_id)

@router.put("/{project_id}", response_model=Project)
def update(project_id: int, update: ProjectUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Pass current_user for permission checks if needed in future
    updated = update_project(db, project_id, update, user_id=int(current_user["id"]))
    if not updated:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated

@router.delete("/{project_id}", response_model=Project)
def remove(project_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    deleted = delete_project(db, project_id, user_id=int(current_user["id"]))
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    return deleted

@router.delete("/{project_id}/members/{user_id}", response_model=ProjectMember)
def remove_user(project_id: int, user_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    deleted = remove_member(db, project_id, user_id, requester_id=int(current_user["id"]))
    if not deleted:
        raise HTTPException(status_code=404, detail="Project_member not found")
    return deleted