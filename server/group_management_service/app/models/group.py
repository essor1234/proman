from sqlalchemy import Column, String, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.sqlite import TEXT
from sqlalchemy.orm import relationship
import uuid
import enum
from datetime import datetime

# Use standard String for SQLite (no native UUID support)
try:
    from sqlalchemy.dialects.postgresql import UUID
    use_uuid = True
except:
    use_uuid = False

from ..core.database import Base


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
    
    # Primary key
    if use_uuid:
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        owner_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    else:
        # For SQLite: store UUID as string
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
    
    # Relationships (optional - uncomment if you want ORM relationships)
    # memberships = relationship("Membership", back_populates="group", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Group(id={self.id}, name={self.name}, owner_id={self.owner_id})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "visibility": self.visibility.value if isinstance(self.visibility, GroupVisibility) else self.visibility,
            "owner_id": str(self.owner_id),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }