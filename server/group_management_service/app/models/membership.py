from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, ForeignKey
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
    
    NOTE: This model only stores user_id (UUID reference).
    To get actual user details (name, email, etc.), you need to:
    1. Create services/user_service.py to call the auth service API
    2. Use user_id to fetch user data from auth service
    
    Example:
        # In controller or route:
        from ..services.user_service import UserService
        
        membership = membership_repo.get_membership(group_id, user_id)
        user_details = await UserService.get_user_by_id(membership.user_id, token)
        # Now you have: {id, username, email, full_name, etc.}
    """
    __tablename__ = "memberships"
    
    # Primary key
    if use_uuid:
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, index=True)
        user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
        invited_by = Column(UUID(as_uuid=True), nullable=True)
    else:
        # For SQLite: store UUID as string
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
    
    # NOTE: user_id and invited_by are just UUID references!
    # They don't contain actual user data (name, email, etc.)
    # 
    # TO GET USER DATA FROM AUTH SERVICE:
    # ===================================
    # 1. Create: services/user_service.py
    #    - This will call auth service API to fetch user details
    # 
    # 2. In your controller/route, import and use:
    #    from ..services.user_service import UserService
    #    
    #    # Fetch single user
    #    user = await UserService.get_user_by_id(membership.user_id, token)
    #    
    #    # Fetch multiple users (for listing members)
    #    user_ids = [m.user_id for m in memberships]
    #    users = await UserService.get_users_by_ids(user_ids, token)
    # 
    # 3. Example in route:
    #    @router.get("/groups/{group_id}/members-with-details")
    #    async def get_members_with_details(
    #        group_id: UUID,
    #        current_user: dict = Depends(get_current_user),
    #        db: Session = Depends(get_db)
    #    ):
    #        # Get memberships (only has user_id)
    #        memberships = membership_repo.list_members(group_id)
    #        
    #        # Fetch actual user data from auth service
    #        user_ids = [m.user_id for m in memberships]
    #        users = await UserService.get_users_by_ids(user_ids, current_user["token"])
    #        
    #        # Combine membership + user data
    #        result = []
    #        for membership in memberships:
    #            user = next((u for u in users if u["id"] == str(membership.user_id)), None)
    #            result.append({
    #                "membership": membership.to_dict(),
    #                "user": user
    #            })
    #        return result
    
    # Timestamps
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships (optional - uncomment if you want ORM relationships)
    # group = relationship("Group", back_populates="memberships")
    
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
    
    class Config:
        # Ensure unique membership per user per group
        __table_args__ = (
            # Uncomment if using PostgreSQL
            # UniqueConstraint('group_id', 'user_id', name='unique_group_user'),
        )