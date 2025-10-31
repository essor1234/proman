from ..schemas.folderFile import FolderFileBase


class FolderFileDB(FolderFileBase, table=True):
    """Database schema for Folder-File association."""
    __tablename__ = "folder_files"
