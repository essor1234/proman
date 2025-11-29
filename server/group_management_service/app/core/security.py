from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Optional

from .config import settings

# 1. auto_error=False allows requests even if the Authorization header is missing
security = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict:
    """
    ⚠️ TEMPORARY TESTING MODE: SECURITY DISABLED ⚠️
    This function now BYPASSES all JWT checks and returns a hardcoded User ID 1.
    """
    
    print("⚠️ GROUP SERVICE SECURITY DISABLED: Returning hardcoded User ID 1")
    
    # Return a dummy user object that matches what your endpoints expect
    return {
        "id": 1,                    # <--- Hardcoded User ID
        "email": "test@example.com",
        "username": "test_user",
        "token": "bypass_token"
    }

    # --- ORIGINAL SECURITY LOGIC (COMMENTED OUT) ---
    # token = credentials.credentials
    # credentials_exception = HTTPException(...)
    # try:
    #    payload = jwt.decode(...)
    #    ...
    # except JWTError as e:
    #    raise credentials_exception


async def get_current_active_user(
    current_user: Dict = Depends(get_current_user)
) -> Dict:
    # Just pass through the hardcoded user
    return current_user


def verify_token(token: str) -> Dict:
    # Return dummy payload for background tasks if needed
    return {"sub": 1, "id": 1}