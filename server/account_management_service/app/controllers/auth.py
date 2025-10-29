from fastapi import APIRouter, HTTPException
from repositories.user_repo import UserRepository
from schemas.auth import RegisterIn

router = APIRouter(prefix="/auth", tags=["auth"])

repo = UserRepository()  # ← No session needed

@router.post("/register")
def register(data: RegisterIn):
    if repo.find_by_email(data.email):
        raise HTTPException(400, "email found")
    
    user = repo.create_user(data.userName, data.email, data.password)
    return {"message": "Registered"}