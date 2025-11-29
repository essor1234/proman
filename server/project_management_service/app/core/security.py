# app/core/security.py

from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict

# security = HTTPBearer() # <--- Comment this out if you want to avoid the "Lock" icon check in Swagger
security = HTTPBearer(auto_error=False) # Use this so it doesn't complain if header is missing

async def get_current_user(
    x_user_id: Optional[str] = Header(None, alias="x-user-id"),
    token_auth: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict:
    
    # --- TEMPORARY TESTING BYPASS ---
    # We just pretend User ID 1 is always logged in.
    print("⚠️ SECURITY DISABLED: Returning hardcoded User ID 1")
    return {"id": 1} 
    # --------------------------------

    # --- COMMENT OUT EVERYTHING BELOW ---
    # credentials_exception = HTTPException(...)
    # if x_user_id: ...
    # try:
    #    token = token_auth.credentials
    #    payload = jwt.decode(...)
    #    ...
    # except ...