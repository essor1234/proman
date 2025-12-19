"""Account Service HTTP Client for File Service"""
import httpx
import os
from typing import Dict, List, Optional

ACCOUNT_SERVICE_URL = os.getenv("ACCOUNT_SERVICE_URL", "http://account_management_service:8001")

async def get_user_details(user_id: int, token: str) -> Optional[Dict]:
    """Fetch user details from Account Service by ID"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{ACCOUNT_SERVICE_URL}/auth/users/{user_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                return response.json()
            else:
                return None
    except Exception as e:
        print(f"Error fetching user {user_id}: {e}")
        return None

async def get_users_batch(user_ids: List[int], token: str) -> Dict[str, Dict]:
    """Fetch multiple users from Account Service"""
    if not user_ids:
        return {}
    
    try:
        ids_str = ",".join(str(id) for id in user_ids)
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{ACCOUNT_SERVICE_URL}/auth/users/batch",
                params={"ids": ids_str},
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {}
    except Exception as e:
        print(f"Error fetching batch users: {e}")
        return {}

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
                return response.json()
            else:
                return []
    except Exception as e:
        print(f"Error searching users: {e}")
        return []
