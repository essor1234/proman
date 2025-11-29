import httpx
import time
from fastapi import HTTPException

GROUP_SERVICE_URL = "http://group_service:8000"

# CHANGED: Added 'token' argument
def get_group_details(group_id: int, token: str = None) -> dict:
    """
    Connects to Group Service to verify if a group exists.
    Passes the JWT token for authentication.
    """
    url = f"{GROUP_SERVICE_URL}/groups/{group_id}"
    
    # Setup Headers with the Token
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    print(f"[Project Service] Calling Group Service -> {url}")

    for attempt in range(1, 7):
        try:
            # CHANGED: Added headers=headers to the request
            response = httpx.get(url, headers=headers, timeout=10.0)
            
            if response.status_code == 404:
                print(f"[Project Service] Group {group_id} not found (404).")
                return None

            if response.status_code == 200:
                return response.json()
            
            # If Group Service returns 401, it means the token is invalid
            if response.status_code == 401:
                raise HTTPException(status_code=401, detail="Group Service rejected the token.")

            print(f"[Project Service] Bad status: {response.status_code} - {response.text}")

        except HTTPException:
            raise # Re-raise HTTP exceptions immediately
        except Exception as e:
            print(f"[Project Service] Attempt {attempt}/6 failed: {type(e).__name__}: {e}")

        if attempt < 6:
            time.sleep(2)

    raise HTTPException(status_code=502, detail="Cannot connect to Group Service")