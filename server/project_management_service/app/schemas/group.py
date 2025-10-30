
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr


# This is the Pydantic schema for API *responses*.
class GroupCreate(BaseModel):
    name: str

class Group(GroupCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

# These are used to create the links between objects.

class UserGroupCreate(BaseModel):
    userId: int
    groupId: int
    role: str

class UserGroup(UserGroupCreate):
    model_config = ConfigDict(from_attributes=True)


class GroupUpdate(BaseModel):
    name: Optional[str] = None

