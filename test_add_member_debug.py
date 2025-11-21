import jwt
import json
from datetime import datetime, timedelta
import requests

SECRET_KEY = "your-secret-key-change-in-production-and-match-auth-service"
ALGORITHM = "HS256"

payload = {
    "sub": "1",
    "username": "testuser",
    "email": "test@example.com",
    "exp": datetime.utcnow() + timedelta(hours=1)
}

token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
headers = {"Authorization": f"Bearer {token}"}
base_url = "http://localhost:8003"

# Create a group first
group_data = {
    "name": "Test Group for Members",
    "description": "Testing member addition",
    "visibility": "private"
}
resp = requests.post(f"{base_url}/groups", json=group_data, headers=headers)
group_id = resp.json()['id']
print(f"Created group: {group_id}\n")

# Try to add a member
print("Adding member to group...")
member_data = {"user_id": "2"}
response = requests.post(f"{base_url}/groups/{group_id}/members", json=member_data, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
