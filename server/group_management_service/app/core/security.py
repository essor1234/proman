import httpx

from typing import Dict
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

ACCOUNT_SERVICE_URL = "http://account_service:8000"

security = HTTPBearer(auto_error=False)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Missing token")

    token = credentials.credentials

    try:
        user_id = int(token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token format")

    url = f"{ACCOUNT_SERVICE_URL}/users/{user_id}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="User not found")
            if response.status_code != 200:
                raise HTTPException(status_code=502, detail="Account service error")
            
            data = response.json()
            return {
                "id": data["id"],
                "username": data.get("username"),
                "email": data.get("email"),
            }
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Cannot reach account service: {e}")

# # 1. auto_error=False allows requests even if the Authorization header is missing
# security = HTTPBearer(auto_error=False)

# async def get_current_user(
#     credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
# ) -> Dict:
#     """
#     ⚠️ TEMPORARY TESTING MODE: SECURITY DISABLED ⚠️
#     This function now BYPASSES all JWT checks and returns a hardcoded User ID 1.
#     """
    
#     print("⚠️ GROUP SERVICE SECURITY DISABLED: Returning hardcoded User ID 1")
    
#     # Return a dummy user object that matches what your endpoints expect
#     return {
#         "id": 1,                    # <--- Hardcoded User ID
#         "email": "test@example.com",
#         "username": "test_user",
#         "token": "bypass_token"
#     }

#     # --- ORIGINAL SECURITY LOGIC (COMMENTED OUT) ---
#     # token = credentials.credentials
#     # credentials_exception = HTTPException(...)
#     # try:
#     #    payload = jwt.decode(...)
#     #    ...
#     # except JWTError as e:
#     #    raise credentials_exception


async def get_current_active_user(
    current_user: Dict = Depends(get_current_user)
) -> Dict:
    # Just pass through the hardcoded user
    return current_user


def verify_token(token: str) -> Dict:
    # Return dummy payload for background tasks if needed
    return {"sub": 1, "id": 1}