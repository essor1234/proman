# project_service/app/repositories/project.py
"""
Repository layer for Project & ProjectMember operations.
"""

from sqlalchemy.orm import Session
from app.models.project import Project as ProjectModel, ProjectMember as ProjectMemberModel
from app.schemas.project import ProjectCreate, ProjectMemberCreate, ProjectUpdate

# CREATE
def create_project(db: Session, project: ProjectCreate):
    db_project = ProjectModel(name=project.name, groupId=project.groupId)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def add_member(db: Session, project_member: ProjectMemberCreate):
    # Validate user
    user = db.query(db.model.User).filter(db.model.User.id == project_member.userId).first()
    if not user:
        raise ValueError(f"User with id {project_member.userId} not found")

    # Validate project
    project = db.query(ProjectModel).filter(ProjectModel.id == project_member.projectId).first()
    if not project:
        raise ValueError(f"Project with id {project_member.projectId} not found")

    # Prevent duplicate
    exists = db.query(ProjectMemberModel).filter(
        ProjectMemberModel.userId == project_member.userId,
        ProjectMemberModel.projectId == project_member.projectId
    ).first()
    if exists:
        raise ValueError("User is already in this project")

    # Insert
    db_project_member = ProjectMemberModel(
        userId=project_member.userId,
        projectId=project_member.projectId,
        role=project_member.role
    )
    db.add(db_project_member)
    db.commit()
    db.refresh(db_project_member)
    return db_project_member

# READ
def get_projects(db: Session, skip: int = 0, limit: int = 100):
    return db.query(ProjectModel).offset(skip).limit(limit).all()

def get_project(db: Session, project_id: int):
    return db.query(ProjectModel).filter(ProjectModel.id == project_id).first()

def get_members(db: Session, project_id: int):
    return db.query(ProjectMemberModel).filter(ProjectMemberModel.projectId == project_id).all()

# UPDATE
def update_project(db: Session, project_id: int, update: ProjectUpdate):
    db_project = get_project(db, project_id)
    if not db_project:
        return None
    if update.name is not None:
        db_project.name = update.name
    if update.groupId is not None:
        db_project.groupId = update.groupId
    db.commit()
    db.refresh(db_project)
    return db_project

# DELETE
def delete_project(db: Session, project_id: int):
    db_project = get_project(db, project_id)
    if db_project:
        db.delete(db_project)
        db.commit()
    return db_project

def remove_member(db: Session, project_id: int, user_id: int):
    project_member = db.query(ProjectMemberModel).filter(
        ProjectMemberModel.projectId == project_id,
        ProjectMemberModel.userId == user_id
    ).first()
    if project_member:
        db.delete(project_member)
        db.commit()
    return project_member