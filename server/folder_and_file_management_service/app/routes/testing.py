from fastapi import APIRouter, Depends, status

from app.core.database import get_db

from app.controllers.getAccountController import (
    get_account_user_logic
)


router = APIRouter(prefix="/testing", tags=["testing"])

@router.get("/user/{user_id}", status_code=status.HTTP_200_OK)
def test_get_account_user(user_id: int):
    # No db needed anymore!
    return get_account_user_logic(user_id)