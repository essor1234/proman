from fastapi import APIRouter, Depends
from controllers.auth import AuthController
from schemas.auth import *

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=RegisterOut)
def register(data: RegisterIn, ctrl: AuthController = Depends()):
    return ctrl.register(data)

@router.post("/login", response_model=LoginOut)
def login(data: LoginIn, ctrl: AuthController = Depends()):
    return ctrl.login(data)

@router.post("/forgot-password", response_model=ForgotOut)
def forgot(data: ForgotIn, ctrl: AuthController = Depends()):
    return ctrl.forgot(data)