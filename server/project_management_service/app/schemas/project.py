from typing import Optional
from pydantic import BaseModel, ConfigDict

class ProjectCreate(BaseModel):
    name: str
    groupId: int # Must be int to match Group Service

class Project(ProjectCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    groupId: Optional[int] = None

class ProjectMemberCreate(BaseModel):
    userId: int
    projectId: int
    role: str

class ProjectMember(ProjectMemberCreate):
    model_config = ConfigDict(from_attributes=True)