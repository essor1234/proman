from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class MVPCreate(BaseModel):
    title: str
    description: Optional[str] = None
    element_id: int

class MVPUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None

class MVP(MVPCreate):
    id: int
    is_completed: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)