from pydantic import BaseModel, EmailStr, Field, validator
import re

class RegisterIn(BaseModel):
    userName: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=8)

    @validator("password")
    def strong(cls, v):
        if not re.search(r"[A-Z]", v): raise ValueError("Uppercase required")
        if not re.search(r"[0-9]", v): raise ValueError("Digit required")
        return v

class RegisterOut(BaseModel): message: str = "Registered"

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class LoginOut(BaseModel): message: str = "Login Success"

class ForgotIn(BaseModel): email: EmailStr
class ForgotOut(BaseModel): message: str = "Go to Forgot password page"