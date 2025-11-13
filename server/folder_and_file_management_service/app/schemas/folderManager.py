
from typing import Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field


"""
Relation with Project Manager
"""
class FolderManagerBase(SQLModel):
    """Schema for FolderManager entity."""
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    folderId: str = Field(..., min_length=1, max_length=255)
    projectid: str = Field(..., min_length=1, max_length=255)   


class FolderManagerCreate(FolderManagerBase):
    pass  # client must send projectid

class FolderManagerRead(FolderManagerBase):
    id: int