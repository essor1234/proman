from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict
# import jwt
# import os

security = HTTPBearer()

# --- JWT Authentication (COMMENTED OUT) ---
# JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
# JWT_ALGORITHM = "HS256"

async def get_current_user(
    token_auth: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    """
    Simple authentication: User enters their user ID as the Bearer token.
    For testing purposes only - NOT for production use!
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid user ID in Bearer token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Get the token value (which should be a user ID number)
        token = token_auth.credentials
        
        # Try to convert to integer
        user_id = int(token)
        
        if user_id <= 0:
            raise credentials_exception
            
        print(f"✅ Authenticated User ID: {user_id}")
        return {"id": user_id}
        
    except ValueError:
        # Token is not a valid integer
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token must be a valid user ID (integer)",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        raise credentials_exception