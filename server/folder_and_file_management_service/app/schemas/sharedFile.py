


"""
Relation with User management
"""

class SharedFile:
    def __init__(self, id: str, fileId: str, sharedWith: str, sharedAt: str):
        self.id = id
        self.fileId = fileId
        self.sharedWith = sharedWith
        self.sharedAt = sharedAt