from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class NoteCreate(BaseModel):
    content: str
    element_id: int

class NoteUpdate(BaseModel):
    content: Optional[str] = None

class Note(NoteCreate):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)