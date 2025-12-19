"""Response schemas for Account Service - Standardized API responses"""
from pydantic import BaseModel, Field
from typing import Optional, List

class UserResponse(BaseModel):
    """Safe user response - no password hash"""
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class AuthResponse(BaseModel):
    """Response for register/login endpoints"""
    message: str
    user_id: int
    username: str
    email: str
    full_name: Optional[str] = None
    access_token: str
    token_type: str = "bearer"

class UserBatchResponse(BaseModel):
    """Response for batch user fetch"""
    __root__: dict[str, UserResponse]

class UsersListResponse(BaseModel):
    """Response for user search"""
    users: List[UserResponse]
    count: int
