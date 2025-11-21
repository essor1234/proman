import jwt
import json
from datetime import datetime, timedelta

# Same secret as in group service
SECRET_KEY = "your-secret-key-change-in-production-and-match-auth-service"
ALGORITHM = "HS256"

# Create a JWT token
payload = {
    "sub": "1",  # user_id
    "username": "testuser",
    "email": "test@example.com",
    "exp": datetime.utcnow() + timedelta(hours=1)
}

token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
print(f"JWT Token: {token}\n")

# Test GET /groups/{id}/members with a group ID from the list
import requests

group_id = "63eb1a38-6f3b-470a-ba52-7d9db3a061b9"
headers = {"Authorization": f"Bearer {token}"}
url = f"http://localhost:8003/groups/{group_id}/members"

response = requests.get(url, headers=headers)
print(f"GET {url}")
print(f"Status: {response.status_code}")
print(f"Response:\n{json.dumps(response.json(), indent=2)}")
