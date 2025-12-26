from typing import Optional, List, Literal
from pydantic import BaseModel, ConfigDict
from .task import Task

class MoscowCreate(BaseModel):
    title: str
    description: Optional[str] = None
    # ✅ NEW: Enforce specific categories using Literal
    category: Literal["Must", "Should", "Could", "Won't"]
    # ✅ NEW: Link to project
    project_id: int
    type: str = "moscow"

class Moscow(MoscowCreate):
    id: int
    tasks: List[Task] = []
    model_config = ConfigDict(from_attributes=True)

class MoscowUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[Literal["Must", "Should", "Could", "Won't"]] = None