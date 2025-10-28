from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Dict

from .config import settings


# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    """
    Validate JWT token and extract user information.
    
    This function validates tokens created by the auth service.
    Both services must share the same JWT_SECRET_KEY.
    
    Returns:
        dict: User information from token payload
        {
            "id": "user-uuid",
            "email": "user@example.com",
            "username": "username",
            "token": "original-token"  # For future API calls to auth service
        }
    
    Raises:
        HTTPException: If token is invalid or expired
    
    Usage in routes:
        @router.get("/groups")
        async def list_groups(
            current_user: dict = Depends(get_current_user),
            db: Session = Depends(get_db)
        ):
            user_id = current_user["id"]
            # ... rest of your code
    """
    token = credentials.credentials
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Extract user ID from 'sub' claim
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        # Return user info from token
        return {
            "id": user_id,
            "email": payload.get("email"),
            "username": payload.get("username"),
            "token": token,  # Pass token along for future auth service API calls
            # Add any other fields your auth service includes in the token
        }
        
    except JWTError as e:
        print(f"JWT Error: {e}")  # Log for debugging
        raise credentials_exception


async def get_current_active_user(
    current_user: Dict = Depends(get_current_user)
) -> Dict:
    """
    Optional: Additional validation for active users.
    You can add extra checks here if needed.
    
    For example:
    - Check if user is banned
    - Check if user email is verified
    - Fetch fresh user data from auth service
    
    Usage:
        @router.get("/groups")
        async def list_groups(
            current_user: dict = Depends(get_current_active_user)
        ):
            # Only active users can access
    """
    # Add additional checks here if needed
    # Example: Check if user is active by calling auth service
    # if not current_user.get("is_active"):
    #     raise HTTPException(status_code=400, detail="Inactive user")
    
    return current_user


def verify_token(token: str) -> Dict:
    """
    Verify and decode a JWT token without FastAPI dependencies.
    Useful for background tasks or non-route functions.
    
    Args:
        token: JWT token string
    
    Returns:
        dict: Decoded token payload
    
    Raises:
        HTTPException: If token is invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )