"""
SQLAlchemy ORM models for Group & UserGroup (junction table).
- Group: Main entity, now uses UUID for external consistency.
- UserGroup: Junction table, now links to UUID.
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

# Import the Base for table creation
from app.core.database import Base 

# FIX: Correct import from sibling module
from .utils import UUIDColumn 


class Group(Base):
    """
    Groups table: Team/collaboration units. Uses UUID as Primary Key.
    """
    __tablename__ = "groups"
    
    # Primary key is now a UUID
    id = UUIDColumn(primary_key=True, index=True) 
    name = Column(String, index=True)

    # Note: 'Project' uses a string to defer resolution (standard SQLAlchemy for cycles)
    projects = relationship("Project", back_populates="group")
    users = relationship("UserGroup", back_populates="group")


class UserGroup(Base):
    """
    Junction table: Many-to-Many between (External) User & (Local) Group.
    - userId: External ID (Integer from Account Service - NO ForeignKey constraint here).
    - groupId: Now uses the local Group UUID.
    """
    __tablename__ = "user_groups"
    
    # userId is the external integer ID (no local FK constraint needed)
    userId = Column(Integer, primary_key=True) 
    
    # groupId is now a UUID Foreign Key to the local Group table
    groupId = Column(String(36), ForeignKey("groups.id"), primary_key=True) 
    
    role = Column(String, default="member", index=True)
    
    # Bidirectional relationship to the local Group
    group = relationship("Group", back_populates="users")