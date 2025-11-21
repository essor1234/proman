from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, ForeignKey, UniqueConstraint # <-- ADD UniqueConstraint
from sqlalchemy.orm import relationship
import uuid
import enum
from datetime import datetime
from typing import TYPE_CHECKING # For type checking if Group is in another file

from ..core.database import Base

# Optional: For type hinting if Group is defined elsewhere
if TYPE_CHECKING:
    from .group import Group


class MembershipRole(str, enum.Enum):
    """Member roles in a group"""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class MembershipStatus(str, enum.Enum):
    """Membership status"""
    ACTIVE = "active"
    PENDING = "pending"
    REMOVED = "removed"


class Membership(Base):
    """
    Membership model representing a user's membership in a group.
    Links users to groups with roles and status.
    """
    __tablename__ = "memberships"
    
    # Primary key - use String(36) for SQLite compatibility
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    group_id = Column(String(36), ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    invited_by = Column(String(36), nullable=True)
    
    # Membership details
    role = Column(
        SQLEnum(MembershipRole),
        default=MembershipRole.MEMBER,
        nullable=False
    )
    
    status = Column(
        SQLEnum(MembershipStatus),
        default=MembershipStatus.ACTIVE,
        nullable=False
    )
    
    # Timestamps
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 🔗 Relationship: Many-to-One
    # The 'group' property provides the ORM linkage back to the Group object.
    group = relationship("Group", back_populates="memberships")
    
    def __repr__(self):
        return f"<Membership(id={self.id}, group_id={self.group_id}, user_id={self.user_id}, role={self.role})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": str(self.id),
            "group_id": str(self.group_id),
            "user_id": str(self.user_id),
            "role": self.role.value if isinstance(self.role, MembershipRole) else self.role,
            "status": self.status.value if isinstance(self.status, MembershipStatus) else self.status,
            "invited_by": str(self.invited_by) if self.invited_by else None,
            "joined_at": self.joined_at.isoformat() if self.joined_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    # 🔑 Data Integrity Constraint
    # Ensures only one Membership exists for a given user in a given group.
    __table_args__ = ( # <-- UNCOMMENTED AND APPLIED
        UniqueConstraint('group_id', 'user_id', name='unique_group_user'),
    )