from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from .task import Task

class MoscowCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: str # Specific required field for Moscow
    type: str = "moscow"

class Moscow(MoscowCreate):
    id: str
    tasks: List[Task] = [] # Nested list of tasks
    model_config = ConfigDict(from_attributes=True)

class MoscowUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None