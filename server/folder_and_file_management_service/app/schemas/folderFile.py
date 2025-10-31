

from typing import Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field




class FolderFileBase(SQLModel):
    """Association schema for Folder and File entities."""
    folderId: int = Field(..., foreign_key="folders.id", primary_key=True)
    fileId: int = Field(..., foreign_key="files.id", primary_key=True)

    
    class config:
        from_attributes = True