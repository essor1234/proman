from http.client import HTTPException
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


security = HTTPBearer()  # Accepts `Authorization: Bearer <token>`

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    # TODO: Replace with real JWT decode
    # For testing: accept any token that is a number
    try:
        user_id = int(token)
        return user_id
    except:
        raise HTTPException(status_code=401, detail="Invalid token")