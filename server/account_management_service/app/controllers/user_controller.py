from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from typing import Dict
from app.core.db import engine
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/{user_id}")
def get_user(user_id: int, current_user: Dict = Depends(get_current_user)):
    """Get user details by ID. Requires authentication."""
    with Session(engine) as session:
        user = session.exec(select(User).where(User.id == user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name
        }
