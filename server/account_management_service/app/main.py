from fastapi import FastAPI
from core.db import init_db
from routes.auth import router

app = FastAPI(title="Auth Service")

app.include_router(router)

@app.on_event("startup")
def start():
    # 1. CREATE TABLES FIRST
    init_db()

    # 2. NOW IMPORT MODELS (after tables exist)
    from sqlmodel import Session, select
    from core.db import engine
    from models.role import Role

    # 3. Seed default role
    with Session(engine) as s:
        if not s.exec(select(Role).where(Role.name == "user")).first():
            s.add(Role(name="user", description="Default user"))
            s.commit()