from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.sqlite import TEXT
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from typing import TYPE_CHECKING

from ..core.database import Base

# Type checking import to avoid circular dependency errors at runtime
if TYPE_CHECKING:
    from .membership import Membership

class GroupVisibility(str, enum.Enum):
    """Enumeration for Group Visibility options."""
    PUBLIC = "public"
    PRIVATE = "private"
    INVITE_ONLY = "invite_only"

class Group(Base):
    """
    SQLAlchemy model representing the 'groups' table.
    """
    __tablename__ = "groups"
    
    # Primary Key: Integer. 
    # In SQLite/SQLAlchemy, 'Integer' + 'primary_key=True' automatically creates an Auto-Incrementing ID.
    id = Column(Integer, primary_key=True, index=True)
    
    # Owner ID is now an Integer to match the user service's likely integer IDs.
    owner_id = Column(Integer, nullable=False, index=True)
    
    # Basic Group Info
    name = Column(String(255), nullable=False, index=True)
    description = Column(TEXT, nullable=True)
    
    # Visibility using the Enum defined above
    visibility = Column(
        SQLEnum(GroupVisibility),
        default=GroupVisibility.PRIVATE,
        nullable=False
    )
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship: One-to-Many
    # This links the Group to the Membership table.
    # cascade="all, delete-orphan": If a group is deleted, delete all its memberships too.
    memberships = relationship(
        "Membership",
        back_populates="group",
        cascade="all, delete-orphan",
        lazy="select"  # Load memberships only when accessed
    ) 
    
    # Calculated Property for Pydantic
    # This allows the API to return 'member_count' without storing it in a database column.
    @property
    def member_count(self) -> int:
        """Returns the number of members in this group."""
        if self.memberships:
            return len(self.memberships)
        return 0

    def __repr__(self):
        return f"<Group(id={self.id}, name={self.name})>"