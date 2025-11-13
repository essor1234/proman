from typing import Optional

from pydantic import Field
from app.models.folderManager import FolderManagerBase


class FolderManager(FolderManagerBase, table=True):
    __tablename__ = "folder_managers"
    id: Optional[int] = Field(default=None, primary_key=True)