from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class TaskCreate(BaseModel):
    description: str
    isFinished: bool = False
    elements_id: str  # Foreign Key linking to Todo or Moscow

class Task(TaskCreate):
    id: str
    model_config = ConfigDict(from_attributes=True)

class TaskUpdate(BaseModel):
    description: Optional[str] = None
    isFinished: Optional[bool] = None