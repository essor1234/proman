"""
JWT Token utilities for Account Management Service.
Standardized JWT creation and validation across services.
"""
import os
from datetime import datetime, timedelta
from typing import Dict, Optional
from jose import jwt, JWTError
from fastapi import HTTPException, status

# JWT Configuration
ALGORITHM = "HS256"
SECRET_KEY = os.environ.get("JWT_SECRET", "my_very_secret_jwt_key")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary to encode in token (e.g., {"user_id": 1, "username": "john"})
        expires_delta: Custom expiration time (default: 30 minutes)
    
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Dict:
    """
    Decode and validate a JWT access token.
    
    Args:
        token: JWT token to decode
    
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException if token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise credentials_exception
