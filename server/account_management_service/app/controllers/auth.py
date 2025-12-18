from fastapi import APIRouter, HTTPException, Form
from sqlmodel import Session, select
from app.models.user import User
from app.core.db import engine
from app.core.security import verify_password, hash_password_secure
from app.core.jwt import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register(username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    with Session(engine) as session:
        existing = session.exec(select(User).where(User.username == username)).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already exists")
        user = User(username=username, email=email, hashed_password=hash_password_secure(password))
        session.add(user)
        session.commit()
        session.refresh(user)
        return {"message": "User registered successfully", "user_id": user.id, "username": user.username}

# JWT-secured login
@router.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == username)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid password")
        payload = {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name
        }
        access_token = create_access_token(payload)
        return {
            "message": "Login successful",
            "token": access_token,
            "user": {
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name
            }
        }