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

# Now test the API with this token
import requests

headers = {"Authorization": f"Bearer {token}"}
url = "http://localhost:8003/groups"

response = requests.get(url, headers=headers)
print(f"GET {url}")
print(f"Status: {response.status_code}")
print(f"Response:\n{json.dumps(response.json(), indent=2)}")
