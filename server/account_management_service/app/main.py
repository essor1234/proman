import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from core.db import init_db, engine  # ← Import engine
from controllers.auth import router
from sqlmodel import select, Session  # ← ADD THIS

# 1. CREATE TABLES FIRST
init_db()

# 2. ADD RELATIONSHIPS
from sqlmodel import Relationship
from models.user import User
from models.role import Role
from models.user_role import UserRole

User.roles = Relationship(back_populates="users", link_model=UserRole)
Role.users = Relationship(back_populates="roles", link_model=UserRole)

app = FastAPI()
app.include_router(router)

@app.on_event("startup")
def start():
    with Session(engine) as s:
        # ← FIX: import select and Session
        if not s.exec(select(Role).where(Role.name == "user")).first():
            s.add(Role(name="user", description="Default user"))
            s.commit()
    print("Auth Service is LIVE!")