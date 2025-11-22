from sqlalchemy import Column, Integer, String, ForeignKey  # <--- Make sure ForeignKey is imported
from sqlalchemy.orm import relationship
from app.core.database import Base
# FIX: Correct import from sibling module
from .utils import UUIDColumn 

class Project(Base):
    """
    Projects table.
    """
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    
    # This remains a plain Integer because Group is in a DIFFERENT microservice
    groupId = Column(Integer, index=True, nullable=False)

    # Relations
    # cascade="all, delete-orphan" cleans up members if the project is deleted
    members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")


class ProjectMember(Base):
    """
    Junction: External User-Project member with roles.
    """
    __tablename__ = "project_members"
    
    userId = Column(Integer, primary_key=True)
    
    # ✅ FIX: You must add ForeignKey("projects.id") here
    projectId = Column(Integer, ForeignKey("projects.id"), primary_key=True) 
    
    role = Column(String, default="member", index=True)
    
    # Relationship to local Project
    project = relationship("Project", back_populates="members")