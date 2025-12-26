import httpx
import time
from fastapi import HTTPException

# Configuration: Docker DNS name for the project service
# Assuming the service in docker-compose is named 'project_service'
PROJECT_SERVICE_URL = "http://project_service:8000"

def get_project_details(project_id: int) -> dict:
    """
    Connects to Project Service to verify if a project exists.
    Implements retry logic (6 attempts).
    """
    url = f"{PROJECT_SERVICE_URL}/projects/{project_id}"
    print(f"[Process Service] Calling Project Service -> {url}")

    for attempt in range(1, 7):  # 1 to 6
        try:
            # Timeout set to 10s
            response = httpx.get(url, timeout=10.0)
            
            # Case: Project does not exist
            if response.status_code == 404:
                print(f"[Process Service] Project {project_id} not found (404).")
                # Return None so the controller can handle the 404 specific message
                return None

            # Case: Success
            if response.status_code == 200:
                data = response.json()
                return {
                    "id": data["id"],
                    "name": data["name"],
                    "groupId": data["groupId"]
                }

            # Case: Server Error
            print(f"[Process Service] Bad status: {response.status_code} - {response.text}")

        except Exception as e:
            # Network errors, connection refused, timeouts
            print(f"[Process Service] Attempt {attempt}/6 failed: {type(e).__name__}: {e}")

        # Wait before retrying
        if attempt < 6:
            time.sleep(2)

    # Final Failure
    raise HTTPException(
        status_code=502, 
        detail="Cannot connect to Project Service after 6 attempts"
    )