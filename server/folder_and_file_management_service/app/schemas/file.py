from typing import Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field
# from ..models.file import FileDB



class FileBase(SQLModel):
    """Base schema for File entity."""
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    userid: int = Field(..., index=True)
    name: str = Field(..., min_length=1, max_length=255)
    size: int = Field(..., gt=0)
    path: str = Field(..., min_length=1)
    date_created: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))


class FileCreate(FileBase):
    """For POST requests—user provides these."""
    model_config = {"deferred": ["id", "date_created", "path", "userid"]} 

class FileRead(FileBase):
    """For GET requests—user receives these."""
    class Config:
        from_attributes = True

class FileUpdate(SQLModel):
    """For PATCH requests—user provides these."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    size: Optional[int] = Field(default=None, gt=0)

class FileDelete(SQLModel):
    """For DELETE requests—user provides these."""
    id: int = Field(..., primary_key=True)