import jwt
import json
from datetime import datetime, timedelta
import os

# Load from env
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-and-match-auth-service")
ALGORITHM = "HS256"
BASE_URL = os.getenv("BASE_URL", "http://localhost:8003")

# Create a JWT token
payload = {
    "sub": "1",  # user_id
    "username": "testuser",
    "email": "test@example.com",
    "exp": datetime.utcnow() + timedelta(hours=1)
}

token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
print(f"JWT Token: {token}\n")

# Test GET /groups/{id}/members with a group ID (replace with your actual ID or fetch dynamically)
import requests

group_id = os.getenv("TEST_GROUP_ID", "63eb1a38-6f3b-470a-ba52-7d9db3a061b9")  # Use env var for flexibility
headers = {"Authorization": f"Bearer {token}"}
url = f"{BASE_URL}/groups/{group_id}/members"

try:
    response = requests.get(url, headers=headers)
    print(f"GET {url}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error: {response.text} (Check if group_id exists)")
except Exception as e:
    print(f"Request failed: {e}")