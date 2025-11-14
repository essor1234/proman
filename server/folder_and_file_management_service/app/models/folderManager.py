# app/models/folderManager.py

from typing import Optional
from sqlmodel import SQLModel, Field

# ← Import from SCHEMAS, not models!
from app.schemas.folderManager import FolderManagerBase

class FolderManager(FolderManagerBase, table=True):
    __tablename__ = "folder_managers"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    folderId: int = Field(foreign_key="folders.id")  # ← explicit FK
    projectid: str = Field(..., index=True)