"""
Test inter-service communication - User enrichment flow
"""
import httpx
import json

BASE_URL_ACCOUNT = "http://localhost:8001"
BASE_URL_PROJECT = "http://localhost:8004"

def log_response(title, response):
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)

# ============================================================
# STEP 1: Create Users in Account Service
# ============================================================
print("\n\n📝 STEP 1: Creating test users...")

users_to_create = [
    {"username": "alice", "email": "alice@example.com", "password": "AlicePass123!", "full_name": "Alice Smith"},
    {"username": "bob", "email": "bob@example.com", "password": "BobPass123!", "full_name": "Bob Johnson"},
    {"username": "charlie", "email": "charlie@example.com", "password": "CharliePass123!", "full_name": "Charlie Brown"},
]

tokens = {}
user_ids = []

for user_data in users_to_create:
    response = httpx.post(
        f"{BASE_URL_ACCOUNT}/auth/register",
        data=user_data
    )
    log_response(f"Register {user_data['username']}", response)
    
    if response.status_code == 200:
        result = response.json()
        tokens[user_data['username']] = result['access_token']
        user_ids.append(result['user_id'])
        print(f"✅ User {user_data['username']} created (ID: {result['user_id']})")

print(f"\n🔑 Tokens: {list(tokens.keys())}")
print(f"👥 User IDs: {user_ids}")

# ============================================================
# STEP 2: Test Account Service Batch Endpoint
# ============================================================
print("\n\n🧪 STEP 2: Testing Account Service batch endpoint...")

alice_token = tokens['alice']
ids_str = ",".join(str(id) for id in user_ids)

response = httpx.get(
    f"{BASE_URL_ACCOUNT}/auth/users/batch",
    params={"ids": ids_str},
    headers={"Authorization": f"Bearer {alice_token}"}
)
log_response("GET /auth/users/batch", response)

# ============================================================
# STEP 3: Create Project with Members
# ============================================================
print("\n\n🏗️ STEP 3: Creating project and adding members...")

# Create project
project_data = {
    "name": "Test Project",
    "groupId": 1
}

response = httpx.post(
    f"{BASE_URL_PROJECT}/projects/",
    json=project_data,
    headers={"Authorization": f"Bearer {alice_token}"}
)
log_response("POST /projects/", response)

if response.status_code == 201:
    project = response.json()
    project_id = project['id']
    print(f"✅ Project created (ID: {project_id})")
    
    # Add members
    print("\n📌 Adding members to project...")
    for uid in user_ids[1:]:  # Skip Alice (she's the owner)
        member_data = {
            "userId": uid,
            "projectId": project_id,
            "role": "member"
        }
        response = httpx.post(
            f"{BASE_URL_PROJECT}/projects/members",
            json=member_data,
            headers={"Authorization": f"Bearer {alice_token}"}
        )
        log_response(f"Add member (userId={uid})", response)
    
    # ============================================================
    # STEP 4: Get Project Members (WITH USER ENRICHMENT)
    # ============================================================
    print("\n\n✨ STEP 4: Getting project members (should have user data)...")
    
    response = httpx.get(
        f"{BASE_URL_PROJECT}/projects/{project_id}/members",
        headers={"Authorization": f"Bearer {alice_token}"}
    )
    log_response("GET /projects/{id}/members", response)
    
    if response.status_code == 200:
        members = response.json()
        print("\n🔍 ANALYZING MEMBER DATA:")
        for member in members:
            print(f"""
  User ID: {member.get('userId')}
  Username: {member.get('username')} ✅ (ENRICHED!)
  Email: {member.get('email')} ✅ (ENRICHED!)
  Full Name: {member.get('full_name')} ✅ (ENRICHED!)
  Role: {member.get('role')}
            """)
        
        # Check if enrichment worked
        has_enrichment = all(
            member.get('username') is not None 
            for member in members
        )
        
        if has_enrichment:
            print("\n✅✅✅ SUCCESS! Inter-service user enrichment is working!")
        else:
            print("\n❌ ERROR: Members don't have username data - enrichment failed")

print("\n\n" + "="*60)
print("🎉 TEST COMPLETE!")
print("="*60)
