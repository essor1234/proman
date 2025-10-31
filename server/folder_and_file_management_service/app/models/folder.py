from ..schemas.folder import FolderBase 


class FolderDB(FolderBase, table=True):
    """Database schema for Folder entity."""
    __tablename__ = "folders"

