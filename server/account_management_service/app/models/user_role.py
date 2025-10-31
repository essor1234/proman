from sqlmodel import SQLModel, Field
from typing import Optional

class UserRole(SQLModel, table=True):
    userId: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)
    roleId: Optional[int] = Field(default=None, foreign_key="role.id", primary_key=True)