# app/schemas/folderFile.py
from sqlmodel import SQLModel, Field
from typing import Optional


class FolderFileBase(SQLModel):
    """Association table: many-to-many Folder ↔ File."""
    folderId: int = Field(..., foreign_key="folders.id", primary_key=True)
    fileId: int = Field(..., foreign_key="files.id", primary_key=True)

    class Config:
        from_attributes = True  # ← Fixed: capital C