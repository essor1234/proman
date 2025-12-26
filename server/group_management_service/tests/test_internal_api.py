import requests
import json
import os

BASE_URL = os.getenv("BASE_URL", "http://localhost:8003")

print("=" * 80)
print("GROUP MANAGEMENT SERVICE - INTERNAL API TESTS")
print("=" * 80)

group_id = None
user_id = "1"

# Test 1: Get all groups
print("\n✅ TEST 1: GET /internal/groups - List all groups")
print("-" * 80)
try:
    response = requests.get(f"{BASE_URL}/internal/groups?page=1&size=10")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Groups returned: {len(data)}")
    if data:
        print(f"First group: {data[0]['name']} (ID: {data[0]['id']})")
        group_id = data[0]['id']  # Use first for subsequent tests
    print("✅ PASS")
except Exception as e:
    print(f"❌ FAIL: {e}")
    print("Skipping tests requiring group_id")

if group_id:
    # Test 2: Get specific group
    print("\n✅ TEST 2: GET /internal/groups/{id} - Get group by ID")
    print("-" * 80)
    try:
        response = requests.get(f"{BASE_URL}/internal/groups/{group_id}")
        print(f"Status: {response.status_code}")
        group = response.json()
        print(f"Group: {group['name']}")
        print(f"Member count: {group['member_count']}")
        print(f"Owner ID: {group['owner_id']}")
        print("✅ PASS")
    except Exception as e:
        print(f"❌ FAIL: {e}")

    # Test 3: Get group members
    print("\n✅ TEST 3: GET /internal/groups/{id}/members - Get group members")
    print("-" * 80)
    try:
        response = requests.get(f"{BASE_URL}/internal/groups/{group_id}/members")
        print(f"Status: {response.status_code}")
        members = response.json()
        print(f"Group: {members['group_name']}")
        print(f"Total members: {members['member_count']}")
        if members['members']:
            print(f"First member: User {members['members'][0]['user_id']} (Role: {members['members'][0]['role']})")
        print("✅ PASS")
    except Exception as e:
        print(f"❌ FAIL: {e}")

    # Test 4: Get member IDs only
    print("\n✅ TEST 4: GET /internal/groups/{id}/members-ids - Get member IDs")
    print("-" * 80)
    try:
        response = requests.get(f"{BASE_URL}/internal/groups/{group_id}/members-ids")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Group ID: {data['group_id']}")
        print(f"Member IDs: {data['member_ids']}")
        print("✅ PASS")
    except Exception as e:
        print(f"❌ FAIL: {e}")

# Test 5: Get user's groups (independent)
print("\n✅ TEST 5: GET /internal/groups/user/{user_id}/groups - Get all groups for a user")
print("-" * 80)
try:
    response = requests.get(f"{BASE_URL}/internal/groups/user/{user_id}/groups")
    print(f"Status: {response.status_code}")
    user_data = response.json()
    print(f"User: {user_id}")
    print(f"Groups count: {user_data['group_count']}")
    if user_data['groups']:
        for i, g in enumerate(user_data['groups'][:3], 1):
            print(f"  {i}. {g['name']} (Role: {g.get('user_role', 'N/A')})")
    print("✅ PASS")
except Exception as e:
    print(f"❌ FAIL: {e}")

# Test 6: Search groups (independent)
print("\n✅ TEST 6: GET /internal/groups/search - Search groups by name")
print("-" * 80)
try:
    response = requests.get(f"{BASE_URL}/internal/groups/search?name=test&limit=5")
    print(f"Status: {response.status_code}")
    search_data = response.json()
    print(f"Search term: {search_data['search_term']}")
    print(f"Results found: {search_data['result_count']}")
    if search_data['groups']:
        for i, g in enumerate(search_data['groups'][:3], 1):
            print(f"  {i}. {g['name']}")
    print("✅ PASS")
except Exception as e:
    print(f"❌ FAIL: {e}")

if group_id:
    # Test 7: Check if user is member
    print("\n✅ TEST 7: GET /internal/groups/check-member/{group_id}/{user_id}")
    print("-" * 80)
    try:
        response = requests.get(f"{BASE_URL}/internal/groups/check-member/{group_id}/1")
        print(f"Status: {response.status_code}")
        check = response.json()
        print(f"Group: {check['group_id']}")
        print(f"User: {check['user_id']}")
        print(f"Is member: {check['is_member']}")
        if check['is_member']:
            print(f"Role: {check['role']}")
        print("✅ PASS")
    except Exception as e:
        print(f"❌ FAIL: {e}")

# Test 8: Get statistics (independent)
print("\n✅ TEST 8: GET /internal/groups/stats - Get system statistics")
print("-" * 80)
try:
    response = requests.get(f"{BASE_URL}/internal/groups/stats")
    print(f"Status: {response.status_code}")
    stats = response.json()
    print(f"Total groups: {stats['total_groups']}")
    print(f"Public groups: {stats['public_groups']}")
    print(f"Private groups: {stats['private_groups']}")
    print(f"Total memberships: {stats['total_memberships']}")
    print(f"Avg group size: {stats['avg_group_size']}")
    print("✅ PASS")
except Exception as e:
    print(f"❌ FAIL: {e}")

print("\n" + "=" * 80)
print("INTERNAL API TEST SUMMARY COMPLETE")
print("=" * 80)