"""Account Service HTTP Client for Project Service"""
import httpx
import os
from typing import Dict, List, Optional
from app.utils.cache import cache

ACCOUNT_SERVICE_URL = os.getenv("ACCOUNT_SERVICE_URL", "http://account_management_service:8001")

async def get_user_details(user_id: int, token: str) -> Optional[Dict]:
    """Fetch user details from Account Service by ID with caching"""
    # Try cache first
    cached = cache.get_user(user_id)
    if cached:
        return cached
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{ACCOUNT_SERVICE_URL}/auth/users/{user_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                data = response.json()
                cache.set_user(user_id, data)  # Cache it
                return data
            else:
                return None
    except Exception as e:
        print(f"Error fetching user {user_id}: {e}")
        return None

async def get_users_batch(user_ids: List[int], token: str) -> Dict[str, Dict]:
    """Fetch multiple users from Account Service with caching"""
    if not user_ids:
        return {}
    
    # Get cached users
    cached_users = cache.get_users_batch(user_ids)
    missing_ids = [id for id in user_ids if str(id) not in cached_users]
    
    if not missing_ids:
        return cached_users  # All cached!
    
    try:
        ids_str = ",".join(str(id) for id in missing_ids)
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{ACCOUNT_SERVICE_URL}/auth/users/batch",
                params={"ids": ids_str},
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                result = response.json()
                cache.set_users_batch(result)  # Cache new ones
                return {**cached_users, **result}  # Merge cached + new
            else:
                return cached_users  # Return what we have cached
    except Exception as e:
        print(f"Error fetching batch users: {e}")
        return cached_users

async def search_users(query: str, token: str) -> List[Dict]:
    """Search users from Account Service"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{ACCOUNT_SERVICE_URL}/auth/users/search",
                params={"q": query},
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                result = response.json()
                # Cache the results
                if isinstance(result, dict) and "users" in result:
                    cache.set_users_batch({str(u["id"]): u for u in result["users"]})
                    return result["users"]
                return result if isinstance(result, list) else []
            else:
                return []
    except Exception as e:
        print(f"Error searching users: {e}")
        return []

