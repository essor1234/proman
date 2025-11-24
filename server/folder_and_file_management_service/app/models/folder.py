# app/models/folder.py
from typing import List
from sqlmodel import SQLModel, Field, Relationship

from ..schemas.folder import FolderBase


class FolderDB(FolderBase, table=True):
    __tablename__ = "folders"

    # Use STRING: "FolderFileDB" instead of importing
    file_links: List["FolderFileDB"] = Relationship(back_populates="folder") # type: ignore