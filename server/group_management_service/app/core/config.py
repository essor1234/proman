from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """
    Application settings.
    Values can be overridden by environment variables or .env file.
    """
    
    # Application Info
    APP_NAME: str = "Group Management Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./group_service.db"
    
    # JWT Settings - MUST MATCH AUTH SERVICE!
    # ==========================================
    # IMPORTANT: Get this value from your auth service team
    # Both services must use the EXACT same secret key
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production-and-match-auth-service"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Auth Service Integration (for future use when fetching user data)
    # ==================================================================
    # When you need to fetch user details from auth service:
    # 1. Set this to your auth service URL
    # 2. Create services/user_service.py
    # 3. Use UserService.get_user_by_id(user_id, token) to fetch user data
    AUTH_SERVICE_URL: str = "http://localhost:8001"
    
    # CORS Settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # Frontend
        "http://localhost:8000",  # API Gateway or other service
        "http://localhost:8001",  # Auth service
        "http://localhost:8002",  # This service
    ]
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()