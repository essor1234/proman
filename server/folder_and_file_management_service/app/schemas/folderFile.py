# app/schemas/folderFile.py
from sqlmodel import SQLModel
from typing import Optional


class FolderFileBase(SQLModel):
    folderId: int
    fileId: int

    class Config:
        from_attributes = True