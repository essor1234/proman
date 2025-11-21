# app/schemas/group_schemas.py
from pydantic import BaseModel, Field, UUID4, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class GroupVisibility(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    INVITE_ONLY = "invite_only"


# === INPUT SCHEMAS ===

class GroupCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name of the group")
    description: Optional[str] = Field(None, max_length=500, description="Group description")
    visibility: GroupVisibility = Field(
        GroupVisibility.PRIVATE,
        description="Who can discover and join the group"
    )

    @validator("name")
    def name_not_empty(cls, v):
        if v.strip() == "":
            raise ValueError("Group name cannot be empty")
        return v.strip()


class GroupUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    visibility: Optional[GroupVisibility] = None

    @validator("name")
    def name_not_empty(cls, v):
        if v is not None and v.strip() == "":
            raise ValueError("Group name cannot be empty")
        return v.strip() if v else None


# === OUTPUT SCHEMAS ===

class GroupResponse(BaseModel):
    id: str  # Stored as string in SQLite
    name: str
    description: Optional[str] = None
    visibility: GroupVisibility
    owner_id: str  # Stored as string in SQLite
    member_count: int = Field(..., ge=0)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Allows conversion from SQLAlchemy model
        orm_mode = True  # Backward compatibility (Pydantic v1)


class GroupListResponse(BaseModel):
    groups: List[GroupResponse]
    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    size: int = Field(..., ge=1, le=100)
    has_more: bool

    class Config:
        from_attributes = True


# Response including member profiles
from app.schemas.membership_schemas import MemberWithProfile


class GroupWithMembersResponse(GroupResponse):
    members: List[MemberWithProfile]

    class Config:
        from_attributes = True