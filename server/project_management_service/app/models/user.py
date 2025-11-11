# project_service/app/models/user.py
"""
SQLAlchemy ORM models for User entity.
- Defines table structure, columns, relationships.
- Relationships enable eager/lazy loading of related data (e.g., groups/projects).
"""

from sqlalchemy import Column, Integer, String  # Column types
from sqlalchemy.orm import relationship  # For foreign key relationships
from core.database import Base  # Inherit from Base for table creation

class User(Base):
    """
    Users table model.
    - Primary table for user accounts.
    - Relationships: Many-to-Many with Groups & Projects via junction tables.
    """
    __tablename__ = "users"  # Maps to 'users' table in DB

    # Primary key: Auto-incrementing integer
    id = Column(Integer, primary_key=True, index=True)
    
    # Indexed for fast lookups (name/email searches)
    name = Column(String, index=True)
    email = Column(String, index=True)

    # Many-to-Many: User belongs to multiple Groups (via UserGroup junction)
    groups = relationship("UserGroup", back_populates="user")
    
    # Many-to-Many: User belongs to multiple Projects (via ProjectMember junction)
    projects = relationship("ProjectMember", back_populates="user")