import requests
import json
import time
import os

AUTH_BASE_URL = os.getenv("AUTH_BASE_URL", "http://localhost:8001")
GROUP_BASE_URL = os.getenv("GROUP_BASE_URL", "http://localhost:8003")

# Give services time to start
time.sleep(2)

# 1. Register a user (use unique username to avoid duplicates)
print("1. Registering user...")
register_url = f"{AUTH_BASE_URL}/auth/register"
unique_username = f"testuser_{int(time.time())}"
params = {
    "username": unique_username,
    "email": f"{unique_username}@example.com",
    "password": "testpass123"
}

try:
    response = requests.post(register_url, params=params)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}\n")
    
    if response.status_code in [200, 201]:
        user_info = response.json()
        print("User registered successfully!\n")
    else:
        print("Registration may have failed (e.g., duplicate); proceeding with login attempt\n")
except Exception as e:
    print(f"Error during registration: {e}\n")

# 2. Login to get JWT token (use the unique username)
print("2. Logging in...")
login_url = f"{AUTH_BASE_URL}/auth/login"
login_params = {
    "username": unique_username,
    "password": "testpass123"
}

try:
    response = requests.post(login_url, params=login_params)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        login_response = response.json()
        token = login_response.get("access_token")
        print(f"✅ Token obtained: {token[:20]}...\n")
        
        # 3. Fetch groups with token
        print("3. Fetching groups...")
        groups_url = f"{GROUP_BASE_URL}/groups"
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(groups_url, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    else:
        print(f"Login failed: {response.status_code}")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")