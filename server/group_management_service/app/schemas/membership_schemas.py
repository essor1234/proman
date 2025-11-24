from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class MembershipRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"

class MembershipCreate(BaseModel):
    """Input for adding a member manually."""
    user_id: int
    role: MembershipRole = MembershipRole.MEMBER

class MembershipUpdate(BaseModel):
    """Input for updating a member's role."""
    role: MembershipRole

class InvitationCreate(BaseModel):
    """Input for sending an invitation."""
    user_id: int
    role: MembershipRole = MembershipRole.MEMBER

class MembershipResponse(BaseModel):
    """Output for membership details."""
    id: int
    group_id: int
    user_id: int
    role: MembershipRole
    status: str
    invited_by: Optional[int] = None
    joined_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
