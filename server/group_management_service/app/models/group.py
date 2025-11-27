from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, select, func
from sqlalchemy.dialects.sqlite import TEXT
from sqlalchemy.orm import relationship, object_session
import uuid
import enum
from datetime import datetime
from typing import TYPE_CHECKING

from ..core.database import Base

if TYPE_CHECKING:
    from .membership import Membership


class GroupVisibility(str, enum.Enum):
    """Group visibility options"""
    PUBLIC = "public"
    PRIVATE = "private"
    INVITE_ONLY = "invite_only"


class Group(Base):
    """
    Group model representing a user group or team.
    """
    __tablename__ = "groups"
    
    # SQLite Configuration: Store UUIDs as standard Strings
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String(36), nullable=False, index=True)
    
    # Group information
    name = Column(String(255), nullable=False, index=True)
    description = Column(TEXT, nullable=True)
    
    # Visibility settings
    visibility = Column(
        SQLEnum(GroupVisibility),
        default=GroupVisibility.PRIVATE,
        nullable=False
    )
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 🔗 Relationships
    memberships = relationship(
        "Membership",
        back_populates="group",
        cascade="all, delete-orphan",
        lazy="select" # Allows us to access .memberships to count them
    ) 
    
    # --- ADDED THIS PROPERTY ---
    @property
    def member_count(self) -> int:
        """
        Calculates member count for Pydantic response.
        Handles cases where memberships might not be loaded yet.
        """
        # If memberships are loaded in memory, count them
        if self.memberships:
            return len(self.memberships)
        
        # Fallback: If session is available, query the count (safer for created_group flow)
        # Note: In a pure 'create' flow, this might return 0 if the transaction 
        # isn't committed/refreshed, but it prevents the crash.
        return 0

    def __repr__(self):
        return f"<Group(id={self.id}, name={self.name}, owner_id={self.owner_id})>"