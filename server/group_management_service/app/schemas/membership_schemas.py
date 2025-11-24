from pydantic import BaseModel, Field, UUID4
from typing import Optional
from datetime import datetime
from enum import Enum


class MembershipRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class MembershipCreate(BaseModel):
    user_id: UUID4
    role: MembershipRole = Field(default=MembershipRole.MEMBER)


class MembershipUpdate(BaseModel):
    role: MembershipRole = Field(..., description="New role for the member")


class InvitationCreate(BaseModel):
    user_id: Optional[UUID4] = None
    role: MembershipRole = MembershipRole.MEMBER


class MembershipResponse(BaseModel):
    id: UUID4
    group_id: UUID4
    user_id: UUID4
    role: MembershipRole
    status: Optional[str] = None
    invited_by: Optional[UUID4] = None
    joined_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
