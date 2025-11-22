"""
SQLAlchemy models for Project & ProjectMember (junction).
- Project: Belongs to optional Group (foreign key now UUID).
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
# FIX: Correct import from sibling module
from .utils import UUIDColumn 

class Project(Base):
    """
    Projects table: Work items, optionally under a Group.
    - Foreign key to groups.id is now a UUID.
    """
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    
    # Foreign key now references the UUID of the Group table
    groupId = Column(String(36), ForeignKey("groups.id"), index=True)  # Nullable FK

    # Relations
    group = relationship("Group", back_populates="projects")
    members = relationship("ProjectMember", back_populates="project")

class ProjectMember(Base):
    """
    Junction: External User-Project member with roles.
    - userId is the external integer ID (no local FK constraint).
    """
    __tablename__ = "project_members"
    
    # userId is the external integer ID (no local FK constraint)
    userId = Column(Integer, primary_key=True) 
    
    projectId = Column(Integer, ForeignKey("projects.id"), primary_key=True)
    role = Column(String, default="member", index=True)
    
    # The relationship to the local User model remains removed.
    project = relationship("Project", back_populates="members")