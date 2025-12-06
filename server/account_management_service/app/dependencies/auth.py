from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.jwt import decode_access_token

jwt_scheme = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(jwt_scheme)):
    token = credentials.credentials
    payload = decode_access_token(token)
    user_data = {
        "user_id": payload.get("user_id"),
        "username": payload.get("username"),
        "email": payload.get("email"),
        "full_name": payload.get("full_name"),
    }
    if not user_data["user_id"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    return user_data