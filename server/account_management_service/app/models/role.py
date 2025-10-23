from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from .user_role import UserRole

class Role(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: str = ""

    # THIS LINE IS REQUIRED
    users: List["User"] = Relationship(
        back_populates="roles",
        link_model=UserRole
    )