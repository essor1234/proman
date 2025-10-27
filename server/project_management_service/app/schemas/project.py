
from pydantic import BaseModel, ConfigDict, EmailStr

class UserCreate(BaseModel):
    name: str
    email: EmailStr


# This is the Pydantic schema for API *responses*.
class User(UserCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class GroupCreate(BaseModel):
    name: str

class Group(GroupCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class ProjectCreate(BaseModel):
    name: str
    groupId: int

class Project(ProjectCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


# These are used to create the links between objects.
class UserGroupCreate(BaseModel):
    userId: int
    groupId: int
    role: str

class UserGroup(UserGroupCreate):
    model_config = ConfigDict(from_attributes=True)

class ProjectMemberCreate(BaseModel):
    userId: int
    projectId: int
    role: str

class ProjectMember(ProjectMemberCreate):
    model_config = ConfigDict(from_attributes=True)

