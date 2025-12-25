import httpx
import time
from fastapi import HTTPException

# Configuration: The internal Docker DNS name for the account service
# Assuming port 8000 based on your team's example
ACCOUNT_SERVICE_URL = "http://account_service:8000"

def get_account_user(user_id: int) -> dict:
    """
    Connects to Account Service to retrieve/verify a user.
    Implements the team's standard retry logic (6 attempts).
    """
    url = f"{ACCOUNT_SERVICE_URL}/users/{user_id}"
    print(f"[Project Service] Calling Account Service -> {url}")

    for attempt in range(1, 7):  # 1 to 6
        try:
            # Timeout set to 10s
            response = httpx.get(url, timeout=10.0)
            
            # Case: User does not exist
            if response.status_code == 404:
                # We raise immediately, no need to retry a 404
                print(f"[Project Service] User {user_id} not found (404).")
                raise HTTPException(status_code=404, detail=f"User {user_id} not found in Account Service")

            # Case: Success
            if response.status_code == 200:
                data = response.json()
                # print(f"[Project Service] User data received: {data}")
                return {
                    "id": data["id"],
                    "name": data.get("name"),
                    "email": data.get("email")
                }

            # Case: Server Error (500, 503, etc)
            print(f"[Project Service] Bad status: {response.status_code} - {response.text}")

        except HTTPException:
            # Re-raise HTTPExceptions (like the 404 above) so they aren't caught by the generic Exception
            raise

        except Exception as e:
            # Network errors, connection refused, timeouts
            print(f"[Project Service] Attempt {attempt}/6 failed: {type(e).__name__}: {e}")

        # Wait before retrying, unless it's the last attempt
        if attempt < 6:
            time.sleep(2)

    # Final Failure
    raise HTTPException(
        status_code=502, 
        detail="Cannot connect to Account Service after 6 attempts"
    )