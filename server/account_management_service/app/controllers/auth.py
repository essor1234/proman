from fastapi import HTTPException, Depends
from sqlmodel import Session
from core.db import get_session
from repositories.user_repo import UserRepository
from schemas.auth import *

class AuthController:
    def __init__(self, session: Session = Depends(get_session)):
        self.repo = UserRepository(session)

    def register(self, data: RegisterIn) -> RegisterOut:
        if self.repo.find_by_email(data.email):
            raise HTTPException(400, "email found")
        user = self.repo.create_user(data.userName, data.email, data.password)
        self.repo.assign_role(user, "user")
        return RegisterOut()

    def login(self, data: LoginIn) -> LoginOut:
        user = self.repo.find_by_email(data.email)
        if not user:
            raise HTTPException(401, "Email invalid")
        if not self.repo.verify_password(data.password, user.password):
            raise HTTPException(401, "Verify password failed")
        return LoginOut()

    def forgot(self, data: ForgotIn) -> ForgotOut:
        if not self.repo.find_by_email(data.email):
            raise HTTPException(404, "Email not registered")
        return ForgotOut()