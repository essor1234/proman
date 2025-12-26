import jwt
import json
from datetime import datetime, timedelta
import os

# Load from env for security
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

# Now test the API with this token
import requests

headers = {"Authorization": f"Bearer {token}"}
url = f"{BASE_URL}/groups"

try:
    response = requests.get(url, headers=headers)
    print(f"GET {url}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Request failed: {e}")