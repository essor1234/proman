# app/controllers/getProjectController.py

import httpx
from fastapi import HTTPException
import time

# Correct service name + internal container port
PROJECT_SERVICE_URL = "http://project_service:8000"

def get_project_logic(project_id: str) -> dict:
    """
    Validate that a project exists in Project Service
    Returns basic project info
    """
    # url = f"{PROJECT_SERVICE_URL}/projects/{project_id}"
    url = f"{PROJECT_SERVICE_URL}/projects/projects/{project_id}"

    print(f"[Folder Service] Calling Project Service → {url}")

    for attempt in range(1, 7):
        try:
            response = httpx.get(url, timeout=10.0)
            # print(f"[Folder Service] Project Status: {response.status_code}")
            print(f"[Folder Service] Project Response: {response.status_code} | {response.text}")

            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Project not found")

            if response.status_code == 200:
                data = response.json()
                print(f"[Folder Service] Project data: {data}")
                return {
                    "id": data["id"],
                    "name": data.get("name"),
                    "owner_id": data.get("owner_id"),  # optional
                }

            print(f"[Folder Service] Bad status: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"[Folder Service] Attempt {attempt}/6 failed: {type(e).__name__}: {e}")

        if attempt < 6:
            time.sleep(2)

    raise HTTPException(
        status_code=502,
        detail="Cannot connect to Project Service after 6 attempts"
    )