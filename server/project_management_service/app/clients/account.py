# project_service/app/clients/account.py

import httpx
from time import sleep
from fastapi import HTTPException

# Configure this URL based on your Docker network setup
ACCOUNT_SERVICE_URL = "http://account_service:8000"

# Define the structure of the data we expect from the AMS
class AccountUserSchema:
    def __init__(self, id: int, name: str, email: str):
        self.id = id
        self.name = name
        self.email = email

def get_account_user(user_id: int) -> AccountUserSchema:
    """
    Calls the external Account Management Service to fetch user details.
    Includes retry logic for transient errors.
    """
    url = f"{ACCOUNT_SERVICE_URL}/users/{user_id}"

    # Use a limited retry mechanism
    for attempt in range(1, 4):  # 3 attempts
        try:
            # Use a short timeout since it's an internal service
            response = httpx.get(url, timeout=5.0)

            if response.status_code == 404:
                # User ID is invalid/not found in the SSOT
                raise HTTPException(status_code=404, detail=f"User ID {user_id} not found in Account Service.")

            if response.status_code == 200:
                data = response.json()
                return AccountUserSchema(
                    id=data["id"],
                    name=data.get("name"),
                    email=data.get("email")
                )

            # Log other non-200/404 statuses (e.g., 500s)
            print(f"[Project Service] AMS Bad status: {response.status_code}")

        except (httpx.RequestError, httpx.HTTPError, ValueError) as e:
            # Catch connection errors, timeouts, or JSON parsing errors
            print(f"[Project Service] AMS Request failed: {type(e).__name__}: {e}")
        
        # Wait before retrying
        if attempt < 3:
            sleep(1)

    # After all retries fail
    raise HTTPException(status_code=503, detail="Account Service is currently unavailable.")