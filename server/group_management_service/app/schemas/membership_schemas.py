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
    user_id: UUID4
    role: MembershipRole = Field(MembershipRole.MEMBER, description="Role in the group")


class MembershipResponse(BaseModel):
    id: UUID4
    group_id: UUID4
    user_id: UUID4
    role: MembershipRole
    joined_at: datetime

    class Config:
        from_attributes = True