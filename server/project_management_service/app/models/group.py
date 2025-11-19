# project_service/app/models/group.py
"""
SQLAlchemy ORM models for Group & UserGroup (junction table).
- Group: Main entity.
- UserGroup: Many-to-Many junction (composite PK: userId + groupId).
"""

from sqlalchemy import Column, Integer, String, ForeignKey  # ForeignKey for relations
from sqlalchemy.orm import relationship
from app.core.database import Base

class Group(Base):
    """
    Groups table: Team/collaboration units.
    - One Group has Many Users (via UserGroup).
    - One Group has Many Projects (one-to-many).
    """
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    
    # Back-populates: Links to junction table
    users = relationship("UserGroup", back_populates="group")
    projects = relationship("Project", back_populates="group")

class UserGroup(Base):
    """
    Junction table: Many-to-Many between User & Group.
    - Composite PK prevents duplicates.
    - Role: 'admin', 'member', etc.
    """
    __tablename__ = "user_groups"
# The User ID is now an external ID, so we remove the ForeignKey constraint.
    userId = Column(Integer, primary_key=True)
    groupId = Column(Integer, ForeignKey("groups.id"), primary_key=True)
    role = Column(String, default="member", index=True)
    
    # Bidirectional relationships

    group = relationship("Group", back_populates="users")