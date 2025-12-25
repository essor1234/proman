# app/models/file.py
from typing import List
from sqlmodel import Field, Relationship
from ..schemas.file import FileBase  # ← Reuse from schema!

class FileDB(FileBase, table=True):
    __tablename__ = "files"

    folder_links: List["FolderFileDB"] = Relationship(back_populates="file") # type: ignore
    