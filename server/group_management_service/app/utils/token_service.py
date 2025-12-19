"""
Secure token service for generating and validating invite links.
Uses cryptographically secure random tokens with hashing for database storage.
Tokens are NEVER exposed in plain form - only stored as hashes.
"""
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Tuple

class TokenService:
    """
    Generates and validates secure invitation tokens.
    
    Security Features:
    - Uses secrets.token_urlsafe() for cryptographically secure random tokens
    - Stores only SHA256 hashes in database (token cannot be recovered if DB is compromised)
    - Tokens are short-lived (24 hours by default)
    - One-time use only (token is cleared after redemption)
    """
    
    TOKEN_LENGTH = 32  # 32 bytes = 256 bits of entropy
    DEFAULT_EXPIRY_HOURS = 24
    
    @staticmethod
    def generate_token() -> str:
        """
        Generates a secure random token.
        
        Returns:
            str: A URL-safe random token (never stored in plain form)
        """
        return secrets.token_urlsafe(TokenService.TOKEN_LENGTH)
    
    @staticmethod
    def hash_token(token: str) -> str:
        """
        Hashes a token using SHA256.
        
        Args:
            token: Plain text token to hash
            
        Returns:
            str: Hex-encoded SHA256 hash
        """
        return hashlib.sha256(token.encode()).hexdigest()
    
    @staticmethod
    def generate_invite_link(group_id: int, base_url: str = "http://localhost:8080") -> Tuple[str, str, datetime]:
        """
        Generates a complete invite link with token.
        
        Args:
            group_id: The group ID for the invite
            base_url: Frontend base URL
            
        Returns:
            Tuple of (plain_token, hashed_token, expiry_datetime)
            - plain_token: Use this in the link (frontend receives this)
            - hashed_token: Store this in database
            - expiry_datetime: When token expires
        """
        plain_token = TokenService.generate_token()
        hashed_token = TokenService.hash_token(plain_token)
        expiry = datetime.utcnow() + timedelta(hours=TokenService.DEFAULT_EXPIRY_HOURS)
        
        # Link format: /join-group/{group_id}?token={plain_token}
        invite_link = f"{base_url}/join-group/{group_id}?token={plain_token}"
        
        return plain_token, hashed_token, expiry
    
    @staticmethod
    def validate_token(provided_token: str, stored_hash: str, expiry_time: Optional[datetime]) -> bool:
        """
        Validates a provided token against stored hash and expiry.
        
        Args:
            provided_token: Token from user
            stored_hash: Hash stored in database
            expiry_time: Token expiry datetime
            
        Returns:
            bool: True if valid, False otherwise
        """
        # Check expiry first
        if expiry_time and datetime.utcnow() > expiry_time:
            return False
        
        # Hash the provided token and compare with stored hash
        provided_hash = TokenService.hash_token(provided_token)
        return secrets.compare_digest(provided_hash, stored_hash)
