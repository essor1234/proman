from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, relationship
import uuid
import enum
from datetime import datetime
from typing import TYPE_CHECKING

from ..core.database import Base

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
    
    # SQLite Configuration: Always use String(36)
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign Keys and IDs must be Strings
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
    
    # 🔗 Relationship
    group: Mapped["Group"] = relationship("Group", back_populates="memberships")

    def __repr__(self):
        return f"<Membership(id={self.id}, group_id={self.group_id}, user_id={self.user_id}, role={self.role})>"
    
    def to_dict(self):
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
    __table_args__ = (
        UniqueConstraint('group_id', 'user_id', name='unique_group_user'),
    )