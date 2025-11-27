from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Re-define Enum for Pydantic (needed for validation)
class GroupVisibility(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    INVITE_ONLY = "invite_only"

# === INPUT SCHEMAS (Data sent by user) ===

class GroupCreate(BaseModel):
    """Schema for creating a new group."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    visibility: GroupVisibility = GroupVisibility.PRIVATE

    # Custom validator to ensure name isn't just whitespace
    @validator("name")
    def name_not_empty(cls, v):
        if v.strip() == "": raise ValueError("Empty name")
        return v.strip()

class GroupUpdate(BaseModel):
    """Schema for updating an existing group."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    visibility: Optional[GroupVisibility] = None

# === OUTPUT SCHEMAS (Data returned to user) ===

class GroupResponse(BaseModel):
    """Schema for returning a single group object."""
    id: int  # Ensure ID is typed as int
    name: str
    description: Optional[str] = None
    visibility: GroupVisibility
    owner_id: int # Ensure owner_id is typed as int
    member_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        # Allows Pydantic to read data from SQLAlchemy models
        from_attributes = True 

class GroupListResponse(BaseModel):
    """Schema for returning a list of groups with pagination."""
    groups: List[GroupResponse]
    total: int
    page: int
    size: int
    has_more: bool

    class Config:
        from_attributes = True