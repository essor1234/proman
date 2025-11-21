from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from app.models.user import User
from app.core.db import engine
from app.core.security import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

# 🧩 REGISTER
@router.post("/register")
def register(username: str, email: str, password: str):
    with Session(engine) as session:
        existing = session.exec(select(User).where(User.username == username)).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already exists")

        user = User(username=username, email=email, hashed_password=hash_password(password))
        session.add(user)
        session.commit()
        session.refresh(user)
        return {"message": "User registered successfully", "user_id": user.id}

# 🔑 LOGIN
@router.post("/login")
def login(username: str, password: str):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == username)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid password")

        return {"message": "Login successful", "user_id": user.id, "username": user.username}
