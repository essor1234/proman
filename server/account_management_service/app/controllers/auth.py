from fastapi import APIRouter, HTTPException, Form, Depends, Query
from sqlmodel import Session, select
from typing import List, Dict
from app.models.user import User
from app.core.db import engine
from app.core.security import verify_password, hash_password_secure, create_access_token, get_current_user
from app.schemas.response import UserResponse, AuthResponse, UsersListResponse

router = APIRouter(prefix="/auth", tags=["auth"])

# 🧩 REGISTER
@router.post("/register", response_model=AuthResponse)
def register(username: str = Form(...), email: str = Form(...), password: str = Form(...), full_name: str = Form(None)):
    with Session(engine) as session:
        existing = session.exec(select(User).where(User.username == username)).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already exists")

        user = User(username=username, email=email, full_name=full_name, hashed_password=hash_password_secure(password))
        session.add(user)
        session.commit()
        session.refresh(user)
        
        # Generate JWT token for new user
        access_token = create_access_token({
            "user_id": user.id,
            "username": user.username,
            "email": user.email
        })
        
        return {
            "message": "User registered successfully",
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "access_token": access_token,
            "token_type": "bearer"
        }

# 🔑 LOGIN
@router.post("/login", response_model=AuthResponse)
def login(username: str = Form(...), password: str = Form(...)):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == username)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid password")

        # Generate JWT token on successful login
        access_token = create_access_token({
            "user_id": user.id,
            "username": user.username,
            "email": user.email
        })
        
        return {
            "message": "Login successful",
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "access_token": access_token,
            "token_type": "bearer"
        }

# 👤 GET USER BY ID
@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, current_user: Dict = Depends(get_current_user)):
    """Get user details by ID. Requires authentication."""
    with Session(engine) as session:
        user = session.exec(select(User).where(User.id == user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user

# 📦 GET BATCH USERS
@router.get("/users/batch")
def get_users_batch(ids: str = Query(...), current_user: Dict = Depends(get_current_user)):
    """Get multiple users by IDs. Format: ?ids=1,2,3"""
    try:
        user_ids = [int(id.strip()) for id in ids.split(",")]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid IDs format. Use comma-separated integers")
    
    with Session(engine) as session:
        users = session.exec(select(User).where(User.id.in_(user_ids))).all()
        
        result = {}
        for user in users:
            result[str(user.id)] = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name
            }
        
        return result

# 🔍 SEARCH USERS
@router.get("/users/search", response_model=UsersListResponse)
def search_users(q: str = Query(...), current_user: Dict = Depends(get_current_user)):
    """Search users by username or email. Format: ?q=john"""
    if len(q) < 2:
        raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")
    
    search_pattern = f"%{q}%"
    with Session(engine) as session:
        users = session.exec(
            select(User).where(
                (User.username.ilike(search_pattern)) | (User.email.ilike(search_pattern))
            ).limit(10)
        ).all()
        
        return {
            "users": users,
            "count": len(users)
        }