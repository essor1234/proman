from ..schemas.file import FileBase


class FileDB(FileBase, table=True):
    """Database schema for File entity."""
    __tablename__ = "files"