from sqlalchemy.orm import Session
from app.models.project import Project, ProjectMember
from app.schemas.project import ProjectCreate, ProjectMemberCreate, ProjectUpdate
from app.core.account_client import get_account_user  # Import the link file

def create_project(db: Session, project: ProjectCreate):
    db_project = Project(name=project.name, groupId=project.groupId)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def get_project(db: Session, project_id: int):
    return db.query(Project).filter(Project.id == project_id).first()

def get_projects(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Project).offset(skip).limit(limit).all()

def update_project(db: Session, project_id: int, project_data: ProjectUpdate):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        return None
    
    # Update fields if they are provided
    if project_data.name:
        db_project.name = project_data.name
    if project_data.groupId is not None:
        db_project.groupId = project_data.groupId
        
    db.commit()
    db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: int):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        return None
    db.delete(db_project)
    db.commit()
    return db_project

def add_member(db: Session, member_data: ProjectMemberCreate):
    """
    Adds a user to a project.
    1. Validates Project exists (Local DB).
    2. Validates User exists (Remote Account Service Call).
    3. Creates relationship.
    """
    # 1. Local Check: Does the project exist?
    project = db.query(Project).filter(Project.id == member_data.projectId).first()
    if not project:
        raise ValueError("Project not found")

    # 2. Remote Check: Does the user exist in Account Service?
    # This uses the link file to call the other service
    # It will raise HTTPException if the user is missing or service is down
    account_user = get_account_user(member_data.userId)
    
    print(f"Adding user {account_user['name']} to project {project.name}")

    # 3. Local Check: Is user already in the project?
    existing_link = db.query(ProjectMember).filter(
        ProjectMember.userId == member_data.userId,
        ProjectMember.projectId == member_data.projectId
    ).first()

    if existing_link:
        raise ValueError("User is already a member of this project")

    # 4. Create the link
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
    # Already renamed to resolve previous import error
    return db.query(ProjectMember).filter(ProjectMember.projectId == project_id).all()

def remove_member(db: Session, project_id: int, user_id: int):
    """
    Removes a member from a project.
    RENAMED from remove_project_member to resolve ImportError.
    """
    member = db.query(ProjectMember).filter(
        ProjectMember.projectId == project_id,
        ProjectMember.userId == user_id
    ).first()
    
    if not member:
        return None
        
    db.delete(member)
    db.commit()
    return member