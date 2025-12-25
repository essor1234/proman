# app/schemas/folderManager.py

from typing import Optional
from sqlmodel import SQLModel

class FolderManagerBase(SQLModel):
    folderId: int  # ← MUST BE int (FK to folders.id)
    projectid: str

class FolderManagerCreate(FolderManagerBase):
    pass

class FolderManagerRead(FolderManagerBase):
    id: int