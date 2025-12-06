from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from app.core.db import engine
from app.models.user import User
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me")
def get_my_info(current_user=Depends(get_current_user)):
    # Just return info from token!
    return current_user

@router.get("/{user_id}")
def get_user(user_id: int, current_user=Depends(get_current_user)):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.id == user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name
        }