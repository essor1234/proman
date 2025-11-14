from http.client import HTTPException
import os
from time import time
from sqlmodel import SQLModel, Field, Session, select

import httpx
from fastapi import HTTPException

"""
Get account user details logic. -> add to create create_file_logic in file.py
"""
# def get_account_user_logic(user_id: int, db: Session) -> dict:
#     # Placeholder logic for retrieving account user details
#     # Replace with actual database queries and logic as needed
#     stmt = select(SQLModel).where(SQLModel.id == user_id)
#     db_user = db.exec(stmt).first()
#     if not db_user:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     return {"id": db_user.id, "username": db_user.username, "email": db_user.email}

# app/controllers/getAccountController.py



ACCOUNT_SERVICE_URL = "http://account_service:8000"

def get_account_user_logic(user_id: int) -> dict:
    url = f"{ACCOUNT_SERVICE_URL}/users/{user_id}"
    print(f"[File Service] Calling Account Service → {url}")

    for attempt in range(1, 7):  # 6 attempts
        try:
            response = httpx.get(url, timeout=10.0)
            print(f"[File Service] Status: {response.status_code}")

            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="User not found in account service")

            if response.status_code == 200:
                data = response.json()
                print(f"[File Service] User data: {data}")
                return {
                    "id": data["id"],
                    "username": data.get("username"),
                    "email": data.get("email"),
                }

            # Any other status (5xx, etc.)
            print(f"[File Service] Bad status: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"[File Service] Attempt {attempt}/6 failed: {type(e).__name__}: {e}")

        if attempt < 6:
            time.sleep(2)

    # After all retries
    raise HTTPException(status_code=502, detail="Cannot connect to account service after 6 attempts")
    
def get_project_id_logic(project_id: int, db: Session) -> dict:
    # Placeholder logic for retrieving project details
    # Replace with actual database queries and logic as needed
    stmt = select(SQLModel).where(SQLModel.id == project_id)
    db_project = db.exec(stmt).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {"id": db_project.id, "name": db_project.name, "description": db_project.description}