# project_service/app/models/project.py
"""
SQLAlchemy models for Project & ProjectMember (junction).
- Project: Belongs to optional Group (foreign key nullable).
- Many-to-Many: Users via ProjectMember.
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Project(Base):
    """
    Projects table: Work items, optionally under a Group.
    """
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    groupId = Column(Integer, ForeignKey("groups.id"), index=True)  # Nullable FK
    
    # Relations
    group = relationship("Group", back_populates="projects")
    members = relationship("ProjectMember", back_populates="project")

class ProjectMember(Base):
    """
    Junction: User-Project member with roles.
    """
    __tablename__ = "project_members"
    userId = Column(Integer, ForeignKey("users.id"), primary_key=True)
    projectId = Column(Integer, ForeignKey("projects.id"), primary_key=True)
    role = Column(String, default="member", index=True)
    
    user = relationship("User", back_populates="projects")
    project = relationship("Project", back_populates="members")