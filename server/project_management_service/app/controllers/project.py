from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.project import Project, ProjectMember
# ✅ FIX: Explicitly import all necessary Pydantic schemas
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectMemberCreate
from app.core.group_client import get_group_details

def create_project(db: Session, project: ProjectCreate, owner_id: int, token: str = None):
    """
    Creates a project after verifying the Group exists via external service.
    Adds the creator as an admin member.
    """
    # 1. External Validation: Check if Group exists in Group Service
    # We pass the token to authorize the request against the Group Service
    print(f"Verifying Group ID {project.groupId}...")
    group_data = get_group_details(project.groupId, token=token)
    
    if not group_data:
        raise HTTPException(status_code=404, detail=f"Group ID {project.groupId} does not exist in Group Service.")

    # 2. Create Local Project
    db_project = Project(
        name=project.name,
        groupId=project.groupId
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    # 3. AUTOMATICALLY Add the Creator as a Member (Admin)
    owner_member = ProjectMember(
        userId=owner_id,
        projectId=db_project.id,
        role="admin"
    )
    db.add(owner_member)
    db.commit()
    
    return db_project

def get_projects(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Project).offset(skip).limit(limit).all()

def get_project(db: Session, project_id: int):
    return db.query(Project).filter(Project.id == project_id).first()

def update_project(db: Session, project_id: int, project_data: ProjectUpdate, user_id: int):
    """
    Updates project details.
    """
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        return None
    
    # Update name if provided
    if project_data.name:
        db_project.name = project_data.name
    
    # Update groupId if provided (Note: Ideally requires validation with token, skipping for now to prevent errors)
    if project_data.groupId is not None:
        # Warning: We are not verifying the new group exists here because we didn't pass the token.
        # If you need validation on update, you must update the route to pass the token here too.
        db_project.groupId = project_data.groupId
        
    db.commit()
    db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: int, user_id: int):
    """
    Deletes a project.
    """
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        return None
        
    # Optional: Check if user_id is admin/owner before deleting?
    
    db.delete(db_project)
    db.commit()
    return db_project

def add_member(db: Session, member_data: ProjectMemberCreate, added_by_id: int):
    """
    Adds a member to the project.
    """
    # 1. Check if project exists
    project = db.query(Project).filter(Project.id == member_data.projectId).first()
    if not project:
        raise ValueError("Project not found")

    # 2. Check if user is already a member
    existing = db.query(ProjectMember).filter(
        ProjectMember.projectId == member_data.projectId,
        ProjectMember.userId == member_data.userId
    ).first()
    
    if existing:
        raise ValueError("User is already a member of this project")

    # 3. Add member
    new_member = ProjectMember(
        userId=member_data.userId,
        projectId=member_data.projectId,
        role=member_data.role 
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return new_member

def get_members(db: Session, project_id: int):
    return db.query(ProjectMember).filter(ProjectMember.projectId == project_id).all()

def remove_member(db: Session, project_id: int, user_id: int, requester_id: int):
    member = db.query(ProjectMember).filter(
        ProjectMember.projectId == project_id,
        ProjectMember.userId == user_id
    ).first()
    
    if not member:
        return None
        
    db.delete(member)
    db.commit()
    return member