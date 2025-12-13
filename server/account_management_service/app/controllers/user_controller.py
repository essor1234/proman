from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from app.core.db import engine
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/{user_id}")
def get_user(user_id: int):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.id == user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
