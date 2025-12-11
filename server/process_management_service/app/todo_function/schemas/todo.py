from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from .task import Task

class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    # ✅ NEW: User must provide the Project ID
    project_id: int 
    type: str = "todo"

class Todo(TodoCreate):
    id: int
    tasks: List[Task] = []
    model_config = ConfigDict(from_attributes=True)

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None