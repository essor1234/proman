from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class TaskCreate(BaseModel):
    description: str
    is_finished: bool = Field(default=False, alias="isFinished")
    elements_id: int 

class Task(TaskCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class TaskUpdate(BaseModel):
    description: Optional[str] = None
    is_finished: Optional[bool] = Field(default=None, alias="isFinished")