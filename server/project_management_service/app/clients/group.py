import httpx
from time import sleep
from fastapi import HTTPException
from uuid import UUID

# Configuration for the external Group Management Service
GROUP_SERVICE_URL = "http://group_management_service:8000/groups" 

class GroupServiceClient:
    def __init__(self, base_url: str = GROUP_SERVICE_URL):
        self.base_url = base_url

    def _make_request(self, method: str, path: str, json: dict = None, params: dict = None, max_attempts: int = 3):
        """Internal utility to handle HTTP request with retry logic."""
        url = f"{self.base_url}{path}"
        print(f"[Project Service] Calling Group Service → {url}")

        for attempt in range(1, max_attempts + 1):
            try:
                # Pass params to httpx.request
                response = httpx.request(method, url, json=json, params=params, timeout=5.0)
                
                if response.status_code == 404:
                    raise HTTPException(status_code=404, detail=f"Resource not found in Group Service at {path}")

                if response.status_code in (200, 201, 204):
                    if response.status_code == 204:
                        return None
                    return response.json()
                
                print(f"[Project Service] Group Service Bad Status {response.status_code}: {response.text}")

            except (httpx.RequestError, httpx.HTTPError, ValueError) as e:
                print(f"[Project Service] Attempt {attempt}/{max_attempts} failed: {type(e).__name__}: {e}")

            if attempt < max_attempts:
                sleep(2) 

        raise HTTPException(status_code=503, detail="Group Service is currently unavailable after multiple attempts")

    def get_group_details(self, group_id: UUID) -> dict:
        """Fetches group details to check existence and user membership/visibility."""
        path = f"/{group_id}"
        return self._make_request("GET", path)

    def add_group_member(self, group_id: UUID, user_id: int, role: str, added_by_user_id: int) -> dict:
        """Adds an external user to an external group via the Group Service."""
        path = f"/{group_id}/members"
        
        # NOTE: The external Group Service route expects `membership_data: MembershipCreate` 
        # with 'user_id' and 'role'. 
        payload = {
            "user_id": str(user_id), 
            "role": role,
            # The 'added_by' is handled by the Group Service's authentication middleware,
            # but we include it in the payload for completeness if the external API expects it.
            "added_by": str(added_by_user_id) 
        }
        
        return self._make_request("POST", path, json=payload)
    
    def list_group_members(self, group_id: UUID, current_user_id: int, status_filter: str | None) -> list[dict]:
        """Lists members of an external group via the Group Service."""
        path = f"/{group_id}/members"
        
        params = {}
        if status_filter:
            params['status_filter'] = status_filter
            
        # We must include the user ID for authorization check in the external service.
        # This is a placeholder as proper auth requires tokens/headers, but we use it for clarity.
        params['user_id'] = str(current_user_id) 

        response = self._make_request("GET", path, params=params)
        return response if response is not None else []