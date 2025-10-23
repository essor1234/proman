from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from .user_role import UserRole

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    userName: str
    email: str = Field(unique=True, index=True)
    password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # THIS LINE IS REQUIRED
    roles: List["Role"] = Relationship(
        back_populates="users",
        link_model=UserRole
    )