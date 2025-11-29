"""
Pydantic schemas for Group entity and its junction table (UserGroup).
Reflects external UUID primary keys.
"""
from typing import Optional
from pydantic import BaseModel, ConfigDict
from uuid import UUID # Import UUID type

# --- Core Group Schemas ---

class GroupCreate(BaseModel):
    """Schema for creating a new Group (Input). ID is auto-generated."""
    name: str
    # Other potential fields like description, visibility, etc.

# FIX: Change 'id' type from int (or implicit) to UUID
class Group(GroupCreate):
    """Schema for Group response (Output)."""
    id: UUID  # <-- FIXED: Now correctly expects a UUID
    model_config = ConfigDict(from_attributes=True)

class GroupUpdate(BaseModel):
    """Schema for updating a Group (Patch)."""
    name: Optional[str] = None
    # Other fields...

# --- User Group (Membership Link) Schemas ---

class UserGroupCreate(BaseModel):
    """Schema for creating a membership link (Input)."""
    # userId is an external integer ID from the Account Service
    userId: int 
    # groupId is the local Group's UUID
    groupId: UUID # <-- FIXED: Must match the Group's new UUID type
    role: str

class UserGroup(UserGroupCreate):
    """Schema for UserGroup response (Output)."""
    model_config = ConfigDict(from_attributes=True)