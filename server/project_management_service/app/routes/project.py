
"""
FastAPI routes for Project CRUD + member.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.project import Project, ProjectCreate, ProjectMember, ProjectMemberCreate, ProjectUpdate
from app.controllers.project import (
    create_project, add_member, get_projects, get_project, get_members,
    update_project, delete_project, remove_member
)

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.post("/", response_model=Project, status_code=status.HTTP_201_CREATED)
def create(project: ProjectCreate, db: Session = Depends(get_db)):
    return create_project(db, project)

@router.post("/members", response_model=ProjectMember)
def add_user(project_member: ProjectMemberCreate, db: Session = Depends(get_db)):
    try:
        return add_member(db, project_member)
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
def update(project_id: int, update: ProjectUpdate, db: Session = Depends(get_db)):
    updated = update_project(db, project_id, update)
    if not updated:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated

@router.delete("/{project_id}", response_model=Project)
def remove(project_id: int, db: Session = Depends(get_db)):
    deleted = delete_project(db, project_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    return deleted

@router.delete("/{project_id}/members/{user_id}", response_model=ProjectMember)
def remove_user(project_id: int, user_id: int, db: Session = Depends(get_db)):
    deleted = remove_member(db, project_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Project_member not found")
    return deleted