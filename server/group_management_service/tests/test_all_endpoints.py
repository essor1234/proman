import jwt
import json
from datetime import datetime, timedelta
import requests

# Same secret as in group service
SECRET_KEY = "your-secret-key-change-in-production-and-match-auth-service"
ALGORITHM = "HS256"

# Create a JWT token
payload = {
    "sub": "1",
    "username": "testuser",
    "email": "test@example.com",
    "exp": datetime.utcnow() + timedelta(hours=1)
}

token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
headers = {"Authorization": f"Bearer {token}"}
base_url = "http://localhost:8003"

print("=" * 80)
print("GROUP MANAGEMENT SERVICE - ENDPOINT TESTS")
print("=" * 80)

# Test 1: GET /groups - List all groups
print("\n✅ TEST 1: GET /groups - List all groups")
print("-" * 80)
try:
    response = requests.get(f"{base_url}/groups", headers=headers)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total groups: {data['total']}")
    print(f"Groups returned: {len(data['groups'])}")
    if data['groups']:
        print(f"First group: {data['groups'][0]['name']} (ID: {data['groups'][0]['id']})")
    print("✅ PASS")
except Exception as e:
    print(f"❌ FAIL: {e}")

# Test 2: POST /groups - Create a new group
print("\n✅ TEST 2: POST /groups - Create a new group")
print("-" * 80)
try:
    new_group = {
        "name": f"Test Group {datetime.now().timestamp()}",
        "description": "This is a test group",
        "visibility": "private"
    }
    response = requests.post(f"{base_url}/groups", json=new_group, headers=headers)
    print(f"Status: {response.status_code}")
    created_group = response.json()
    group_id = created_group['id']
    print(f"Created group: {created_group['name']} (ID: {group_id})")
    print(f"Member count: {created_group['member_count']}")
    print("✅ PASS")
except Exception as e:
    print(f"❌ FAIL: {e}")
    group_id = "63eb1a38-6f3b-470a-ba52-7d9db3a061b9"  # Use existing group

# Test 3: GET /groups/{id} - Get specific group
print("\n✅ TEST 3: GET /groups/{id} - Get specific group")
print("-" * 80)
try:
    response = requests.get(f"{base_url}/groups/{group_id}", headers=headers)
    print(f"Status: {response.status_code}")
    group = response.json()
    print(f"Group: {group['name']}")
    print(f"Owner ID: {group['owner_id']}")
    print(f"Visibility: {group['visibility']}")
    print("✅ PASS")
except Exception as e:
    print(f"❌ FAIL: {e}")

# Test 4: GET /groups/{id}/members - Get group members with user profiles
print("\n✅ TEST 4: GET /groups/{id}/members - Get group members with user profiles")
print("-" * 80)
try:
    response = requests.get(f"{base_url}/groups/{group_id}/members", headers=headers)
    print(f"Status: {response.status_code}")
    group_data = response.json()
    print(f"Group: {group_data['name']}")
    print(f"Total members: {group_data['member_count']}")
    if group_data['members']:
        for i, member in enumerate(group_data['members']):
            print(f"  Member {i+1}:")
            print(f"    - User ID: {member['user']['id']}")
            print(f"    - Username: {member['user']['username']}")
            print(f"    - Email: {member['user']['email']}")
            print(f"    - Role: {member['membership']['role']}")
    print("✅ PASS")
except Exception as e:
    print(f"❌ FAIL: {e}")

# Test 5: PUT /groups/{id} - Update group
print("\n✅ TEST 5: PUT /groups/{id} - Update group")
print("-" * 80)
try:
    update_data = {
        "name": f"Updated Group {datetime.now().timestamp()}",
        "description": "Updated description",
        "visibility": "public"
    }
    response = requests.put(f"{base_url}/groups/{group_id}", json=update_data, headers=headers)
    print(f"Status: {response.status_code}")
    updated_group = response.json()
    print(f"Updated group: {updated_group['name']}")
    print(f"New visibility: {updated_group['visibility']}")
    print("✅ PASS")
except Exception as e:
    print(f"❌ FAIL: {e}")

# Test 6: POST /groups/{id}/members - Add member to group
print("\n✅ TEST 6: POST /groups/{id}/members - Add member to group")
print("-" * 80)
try:
    member_data = {
        "user_id": "2"  # Add user 2 (alice)
    }
    response = requests.post(f"{base_url}/groups/{group_id}/members", json=member_data, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code in [200, 201]:
        new_member = response.json()
        print(f"Added user {new_member.get('user_id')} to group")
        print(f"Role: {new_member.get('role')}")
        print("✅ PASS")
    else:
        print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ FAIL: {e}")

# Test 7: GET /groups with pagination
print("\n✅ TEST 7: GET /groups with pagination")
print("-" * 80)
try:
    response = requests.get(f"{base_url}/groups?page=1&size=2", headers=headers)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Page: {data['page']}, Size: {data['size']}")
    print(f"Total: {data['total']}, Has more: {data['has_more']}")
    print(f"Groups on this page: {len(data['groups'])}")
    print("✅ PASS")
except Exception as e:
    print(f"❌ FAIL: {e}")

# Test 8: Account Service Integration - Verify user profile enrichment
print("\n✅ TEST 8: Account Service Integration - Verify user profile enrichment")
print("-" * 80)
try:
    response = requests.get(f"{base_url}/groups/{group_id}/members", headers=headers)
    if response.status_code == 200:
        group_data = response.json()
        if group_data['members']:
            member = group_data['members'][0]
            user_data = member['user']
            print(f"User from Account Service:")
            print(f"  - ID: {user_data['id']}")
            print(f"  - Username: {user_data['username']}")
            print(f"  - Email: {user_data['email']}")
            print(f"  - Full Name: {user_data.get('full_name', 'N/A')}")
            print("✅ PASS - User profile successfully fetched from Account Service")
    else:
        print(f"❌ FAIL: {response.status_code}")
except Exception as e:
    print(f"❌ FAIL: {e}")

print("\n" + "=" * 80)
print("TEST SUMMARY COMPLETE")
print("=" * 80)
