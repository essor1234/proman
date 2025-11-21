from typing import Optional

import httpx
from fastapi import HTTPException, status

from app.core.config import settings


def get_user_by_id(user_id: str, token: Optional[str] = None, timeout: float = 5.0) -> Optional[dict]:
    """
    Fetch a user from the Account Management Service.

    Args:
        user_id: The user id to fetch (string or int as string).
        token: Optional JWT token to forward for authorization.
        timeout: Request timeout in seconds.

    Returns:
        dict: user JSON if found
        None: if user not found (404)

    Raises:
        HTTPException: on network errors, auth errors or upstream failures.
    """

    # Prefer ACCOUNT_SERVICE_URL, fall back to AUTH_SERVICE_URL for backwards compatibility
    base_url = getattr(settings, "ACCOUNT_SERVICE_URL", None) or getattr(settings, "AUTH_SERVICE_URL")
    if not base_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Account service URL not configured"
        )

    url = f"{base_url.rstrip('/')}/users/{user_id}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        resp = httpx.get(url, headers=headers, timeout=timeout)
    except httpx.RequestError as exc:
        # Network-level errors
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Could not reach account service: {exc}"
        )

    if resp.status_code == 200:
        try:
            data = resp.json()
            # Ensure id is a string for consistency with our schema
            if data and 'id' in data:
                data['id'] = str(data['id'])
            return data
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Invalid JSON returned from account service"
            )
    elif resp.status_code == 404:
        return None
    elif resp.status_code == 401:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized to fetch user from account service")
    else:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Account service returned error: {resp.status_code}"
        )
