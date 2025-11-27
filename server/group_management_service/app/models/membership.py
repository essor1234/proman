from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, relationship
import enum
from datetime import datetime
from typing import TYPE_CHECKING

from ..core.database import Base

if TYPE_CHECKING:
    from .group import Group

class MembershipRole(str, enum.Enum):
    """Roles a user can have within a group."""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"

class MembershipStatus(str, enum.Enum):
    """Status of the membership (e.g., waiting for approval vs active)."""
    ACTIVE = "active"
    PENDING = "pending"
    REMOVED = "removed"

class Membership(Base):
    """
    SQLAlchemy model representing the 'memberships' table.
    Acts as a link between Users and Groups.
    """
    __tablename__ = "memberships"
    
    # Auto-incrementing Integer ID for the membership record itself
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key: Links to groups.id.
    # ondelete="CASCADE": If the group is deleted in DB, this record vanishes.
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # User ID: Stored as Integer (assuming User Service uses Int IDs)
    user_id = Column(Integer, nullable=False, index=True)
    
    # Who sent the invite? (Optional, Integer)
    invited_by = Column(Integer, nullable=True)
    
    # State fields (Role and Status)
    role = Column(SQLEnum(MembershipRole), default=MembershipRole.MEMBER, nullable=False)
    status = Column(SQLEnum(MembershipStatus), default=MembershipStatus.ACTIVE, nullable=False)
    
    # Timestamps
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship back to the Group model
    group: Mapped["Group"] = relationship("Group", back_populates="memberships")

    def __repr__(self):
        return f"<Membership(id={self.id}, group_id={self.group_id}, user_id={self.user_id})>"
    
    # Constraint: A user can only have ONE membership record per group.
    __table_args__ = (
        UniqueConstraint('group_id', 'user_id', name='unique_group_user'),
    )