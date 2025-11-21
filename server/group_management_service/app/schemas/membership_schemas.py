# app/schemas/membership_schemas.py
from pydantic import BaseModel, Field, UUID4
from typing import Optional, List
from datetime import datetime
from enum import Enum


class MembershipRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class MembershipCreate(BaseModel):
    user_id: str  # Stored as string in SQLite
    role: MembershipRole = Field(MembershipRole.MEMBER, description="Role in the group")


class MembershipUpdate(BaseModel):
    role: MembershipRole = Field(..., description="New role for the member")


class MembershipResponse(BaseModel):
    id: str  # Stored as string in SQLite
    group_id: str  # Stored as string in SQLite
    user_id: str  # Stored as string in SQLite
    role: MembershipRole
    joined_at: datetime

    class Config:
        from_attributes = True


# --- Additional helper schemas for enriched responses ---
class UserProfile(BaseModel):
    id: str  # From Account service, stored as UUID in their DB
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None


class MemberWithProfile(BaseModel):
    membership: MembershipResponse
    user: Optional[UserProfile] = None

    class Config:
        from_attributes = True