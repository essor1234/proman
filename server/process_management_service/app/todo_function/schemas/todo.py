
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from .task import Task
class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    type: str = "todo"

class Todo(TodoCreate):
    id: str
    tasks: List[Task] = []  # Nested list of tasks
    model_config = ConfigDict(from_attributes=True)

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None