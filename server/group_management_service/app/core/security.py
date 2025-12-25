import os
from typing import Dict
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

ALGORITHM = "HS256"
SECRET_KEY = os.environ.get("JWT_SECRET", "my_very_secret_jwt_key")

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

# Remove ACCOUNT_SERVICE_URL - no longer needed
security = HTTPBearer(auto_error=False)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Missing token")

    token = credentials.credentials

    # Replace the entire HTTP call logic with JWT decoding
    try:
        payload = decode_access_token(token)
        return {
            "id": payload.get("user_id"),  # Note: map "user_id" from token to "id"
            "username": payload.get("username"),
            "email": payload.get("email"),
            "full_name": payload.get("full_name"),  # Add this if needed
        }
    except Exception as e:
        # Handle JWT decode errors (expired, invalid signature, etc.)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=f"Invalid or expired token: {str(e)}"
        )

async def get_current_active_user(
    current_user: Dict = Depends(get_current_user)
) -> Dict:
    # Keep as-is - just passes through the user from token
    return current_user

def verify_token(token: str) -> Dict:
    # Update to use actual JWT decoding instead of dummy data
    try:
        payload = decode_access_token(token)
        return {
            "sub": payload.get("user_id"),
            "id": payload.get("user_id"),
            "username": payload.get("username"),
            "email": payload.get("email"),
        }
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )