# app/models/folder_file.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional


class FolderFileDB(SQLModel, table=True):
    __tablename__ = "folder_files"

    folderId: int = Field(..., foreign_key="folders.id", primary_key=True)
    fileId: int = Field(..., foreign_key="files.id", primary_key=True)

    # Use STRING: "FolderDB" and "FileDB"
    folder: Optional["FolderDB"] = Relationship(back_populates="file_links")
    file: Optional["FileDB"] = Relationship(back_populates="folder_links")