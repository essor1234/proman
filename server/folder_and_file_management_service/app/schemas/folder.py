
from typing import Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field
from .folderFile import FolderFileBase


class FolderBase(SQLModel):
    """Base schema for Folder entity."""
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    name: str = Field(..., min_length=1, max_length=255)
    path: str = Field(..., min_length=1)

class FolderCreate(FolderBase):
    """For POST requests—user provides these."""
    id: Optional[int] = None

class FolderRead(FolderBase):
    """For GET requests—user receives these."""
    id: Optional[int] = None
    file_links: Optional[list[FolderFileBase]] = []
    class Config:
        from_attributes = True

class FolderUpdate(SQLModel):
    """For PATCH requests—user provides these."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)

class FolderDelete(SQLModel):
    """For DELETE requests—user provides these."""
    id: int = Field(..., primary_key=True)