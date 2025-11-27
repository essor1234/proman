from pydantic import BaseModel, Field, validator
from typing import Optional, List, Union
from datetime import datetime
from enum import Enum
import uuid

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
    # Changed UUID4 to str to allow compatibility with SQLite Strings and your '1' test ID
    id: str 
    name: str
    description: Optional[str] = None
    visibility: GroupVisibility
    owner_id: str 
    member_count: int = Field(default=0, ge=0) # Added default to be safe
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 
        orm_mode = True 

    # Optional: Validator to ensure output looks clean if you want to force UUID format later
    @validator('id', 'owner_id', pre=True)
    def parse_ids(cls, v):
        return str(v)


class GroupListResponse(BaseModel):
    groups: List[GroupResponse]
    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    size: int = Field(..., ge=1, le=100)
    has_more: bool

    class Config:
        from_attributes = True