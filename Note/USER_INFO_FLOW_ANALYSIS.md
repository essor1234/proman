# 🔄 User Info Flow Analysis: 4-Service Architecture

**Analysis Date:** December 19, 2025

---

## Current User Information Flow

### Service Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INFO MANAGEMENT                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Account Service      Project Service    Group Service          │
│  ┌─────────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │                 │  │              │  │              │       │
│  │  Stores:        │  │  Stores:     │  │  Stores:     │       │
│  │  - id           │  │  - userId    │  │  - owner_id  │       │
│  │  - username     │  │  - role      │  │  - user_id   │       │
│  │  - email        │  │  - (no name) │  │  - (no name) │       │
│  │  - password     │  │              │  │              │       │
│  │                 │  │  Problem:    │  │  Problem:    │       │
│  │  ✅ Complete    │  │  ❌ Duplica- │  │  ❌ Duplica- │       │
│  │     user data   │  │     tion     │  │     tion     │       │
│  │                 │  │  ❌ Missing  │  │  ❌ Missing  │       │
│  │                 │  │     username │  │     username │       │
│  │                 │  │     email    │  │     email    │       │
│  │                 │  │              │  │              │       │
│  └─────────────────┘  └──────────────┘  └──────────────┘       │
│                                                                  │
│  File Service                                                   │
│  ┌──────────────────────────────────────────────────────┐      │
│  │                                                      │      │
│  │  Stores:                                             │      │
│  │  - None (no user info at all)                        │      │
│  │                                                      │      │
│  │  Problem:                                            │      │
│  │  ❌ Can't track file ownership                       │      │
│  │  ❌ Can't enforce access control                     │      │
│  │                                                      │      │
│  └──────────────────────────────────────────────────────┘      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## ⚠️ Current Problems

### Problem #1: No Inter-Service User Queries

**Current State:**
```python
# Account Service
stores: User(id, username, email, hashed_password)

# Project Service  
stores: ProjectMember(userId, projectId, role)  # Just IDs!
# Has userId but NOT username, email, etc.

# Group Service
stores: Membership(user_id, group_id, role)     # Just IDs!
# Has user_id but NOT username, email, etc.

# How do they get user details?
# Answer: ❌ THEY DON'T!
```

**When You Need User Info:**
```
Scenario: Get all members of a project
API Call: GET /projects/1/members

Expected Response:
[
  {
    "userId": 1,
    "username": "john",        ← Where does this come from?
    "email": "john@example.com" ← Where does this come from?
    "role": "admin"
  }
]

Current Response (Incomplete):
[
  {
    "userId": 1,
    "role": "admin"
    # ❌ Missing username & email!
  }
]
```

**Why It Matters:**
- Frontend cannot display user names in lists
- Can't show "john" → only shows user ID "1"
- Poor user experience
- Breaks features like "Invite User X to Project"

---

### Problem #2: No Service-to-Service API Calls

**Current Implementation:**
```python
# Project Service routes/project.py
class ProjectMember(Base):
    userId = Column(Integer)  # Just a number!
    # No way to look up user details

# Group Service routes/membership.py
class Membership(Base):
    user_id = Column(Integer)  # Just a number!
    # No way to look up user details

# File Service
# Stores files but has NO user_id tracking at all!
```

**What Should Happen:**
```python
# When Project Service needs user info:
from httpx import AsyncClient

@router.get("/projects/1/members")
async def get_members(project_id: int):
    members = db.query(ProjectMember).filter(...).all()
    
    # Need to enrich with user data:
    for member in members:
        # Call Account Service to get user details
        async with AsyncClient() as client:
            resp = await client.get(
                f"http://account_service:8000/users/{member.userId}",
                headers={"Authorization": f"Bearer {jwt_token}"}
            )
            user_data = resp.json()
            member.username = user_data["username"]
            member.email = user_data["email"]
    
    return members
```

**Problem:** ❌ This code DOESN'T EXIST in any service!

---

## 📊 What Each Service Stores About Users

### Account Service ✅
```python
User {
  id: int              ✅ PK
  username: str        ✅ Unique username
  email: str           ✅ User email
  hashed_password: str ✅ Encrypted password
}
```
**Completeness:** 100% - Has everything

---

### Project Service ⚠️
```python
ProjectMember {
  userId: int          ✅ FK to user
  projectId: int       ✅ FK to project
  role: str            ✅ Member role
  # Missing:
  # username: str      ❌
  # email: str         ❌
}

Project {
  id: int              ✅ PK
  name: str            ✅ Project name
  description: str     ✅ Project description
  groupId: int         ✅ FK to group (external service)
  # Missing:
  # owner_id: int      ❌ Who created the project?
  # created_by_name    ❌ Can't display creator
}
```
**Completeness:** ~50% - Missing user name & email

---

### Group Service ⚠️
```python
Membership {
  user_id: int         ✅ FK to user
  group_id: int        ✅ FK to group
  role: str            ✅ Member role
  status: str          ✅ Active/Pending
  invited_by: int      ✅ Who invited them
  # Missing:
  # username: str      ❌
  # email: str         ❌
}

Group {
  id: int              ✅ PK
  owner_id: int        ✅ FK to user
  name: str            ✅ Group name
  description: str     ✅ Description
  # Missing:
  # owner_name: str    ❌ Can't display owner
  # owner_email: str   ❌
}
```
**Completeness:** ~60% - Missing user names & emails

---

### File Service ❌
```python
# Checking... routes/file.py, routes/folder.py
# ❌ NO USER TRACKING AT ALL!
# 
# Missing:
# owner_id: int        ❌
# created_by: str      ❌
# No way to track who owns a file
# No way to enforce access control
```
**Completeness:** 0% - No user info stored

---

## 🔄 Recommended User Info Flow

### Option 1: Call Account Service When Needed (Recommended)

```
When you need user details:

Project Service
    ↓ GET /users/1
Account Service ✅ Returns full user data
    ↓ {"id": 1, "username": "john", "email": "..."}
Project Service stores in response
```

**Pros:**
- ✅ Single source of truth (Account Service)
- ✅ Always up-to-date user info
- ✅ No data duplication

**Cons:**
- ⚠️ Extra network call per user
- ⚠️ Slower responses if many users

**Implementation:**
```python
# project_management_service/app/utils/account_client.py
import httpx
import os

ACCOUNT_SERVICE_URL = os.environ.get("ACCOUNT_SERVICE_URL", "http://account_service:8000")

async def get_user_details(user_id: int, jwt_token: str):
    """Fetch user details from Account Service"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{ACCOUNT_SERVICE_URL}/users/{user_id}",
            headers={"Authorization": f"Bearer {jwt_token}"},
            timeout=5.0
        )
        if response.status_code == 200:
            return response.json()
        return {"id": user_id, "username": f"User#{user_id}"}  # Fallback


# In routes/project.py
@router.get("/projects/{project_id}/members")
async def get_members(
    project_id: int,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    members = db.query(ProjectMember).filter(...).all()
    
    # Enrich with user data
    enriched = []
    for member in members:
        user_details = await get_user_details(member.userId, current_user["token"])
        enriched.append({
            "user_id": member.userId,
            "username": user_details.get("username"),
            "email": user_details.get("email"),
            "role": member.role
        })
    
    return enriched
```

---

### Option 2: Cache User Info Locally (Performance)

```
First time accessing user:
    ↓
Call Account Service
    ↓
Cache in Redis for 1 hour
    ↓
Subsequent calls use cache

After 1 hour:
    ↓
Refresh from Account Service
```

**Pros:**
- ✅ Fast (cache hits)
- ✅ Reduces load on Account Service
- ✅ Works if Account Service is slow

**Cons:**
- ⚠️ Stale data (if user changes name, takes 1 hour to update)
- ⚠️ Extra complexity

---

### Option 3: Denormalize (Copy User Data)

```
When user details needed:
    ↓
Store in Project/Group service:
{
  "user_id": 1,
  "username": "john",          ← Copied from Account Service
  "email": "john@example.com"  ← Copied from Account Service
}

When user updates their profile:
    ↓
Account Service notifies others (event-driven)
    ↓
Project/Group services update their copies
```

**Pros:**
- ✅ Fast (no extra calls)
- ✅ Works offline

**Cons:**
- ⚠️ Data duplication
- ⚠️ Risk of inconsistency
- ⚠️ Complex sync logic

---

## 🎯 Current User Flow Issues

### Scenario 1: Display Project Members

**API:** `GET /projects/1/members`

**Current Response:**
```json
[
  {
    "userId": 1,
    "role": "admin"
  },
  {
    "userId": 2,
    "role": "member"
  }
]
```
❌ Frontend shows: "User 1", "User 2" (useless!)

**Should Be:**
```json
[
  {
    "userId": 1,
    "username": "john",
    "email": "john@example.com",
    "role": "admin"
  },
  {
    "userId": 2,
    "username": "sarah",
    "email": "sarah@example.com",
    "role": "member"
  }
]
```
✅ Frontend shows: "john (admin)", "sarah (member)"

---

### Scenario 2: Display Group Members

**API:** `GET /groups/1/members`

**Current Response:**
```json
[
  {
    "user_id": 1,
    "role": "owner",
    "status": "active"
  }
]
```
❌ Can't display who the owner is!

**Should Be:**
```json
[
  {
    "user_id": 1,
    "username": "john",
    "email": "john@example.com",
    "role": "owner",
    "status": "active"
  }
]
```
✅ Can display "john is the owner"

---

### Scenario 3: Invite User to Group

**What Happens Now:**
```
Frontend: "Invite user to group"
Input: User ID (just a number)
Send: POST /groups/1/invite { "user_id": 2 }
✅ Works technically
❌ UX is terrible (can't search by username)
```

**What Should Happen:**
```
Frontend: "Invite user to group"
User types: "sa..."
Frontend searches Account Service for matching users
Dropdown shows: "sarah (sarah@example.com)", "sam (sam@example.com)"
User clicks: "sarah"
Send: POST /groups/1/invite { "user_id": 2 }
✅ Good UX
```

**Requires:**
- Frontend to have endpoint to search users
- Account Service to provide `GET /users/search?q=sa`

---

## 📋 Implementation Checklist

### Phase 1: Enable Inter-Service User Queries

**Account Service:**
- [ ] Create `GET /users/{user_id}` endpoint (public)
- [ ] Requires JWT authentication
- [ ] Returns: `{"id", "username", "email", "created_at"}`
- [ ] Returns 404 if user doesn't exist

**Project Service:**
- [ ] Import `account_client` utility
- [ ] On member endpoints: fetch user details from Account Service
- [ ] Cache user data for 5 minutes

**Group Service:**
- [ ] Import `account_client` utility
- [ ] On member endpoints: fetch user details from Account Service
- [ ] Cache user data for 5 minutes

**File Service:**
- [ ] Add `owner_id` field to files/folders
- [ ] Add `created_by` field for display
- [ ] Query Account Service for owner details

---

### Phase 2: User Search

**Account Service:**
- [ ] Create `GET /users/search?q=john` endpoint
- [ ] Returns: `[{"id": 1, "username": "john", "email": "..."}]`
- [ ] Limit results to 10

**Frontend:**
- [ ] Implement user search dropdown
- [ ] Call Account Service search endpoint

---

### Phase 3: User Profile Updates

**Account Service:**
- [ ] Add `PUT /users/{user_id}` endpoint
- [ ] Can update: username, email, password
- [ ] Publish event to other services (optional)

**Other Services:**
- [ ] If using cache: invalidate on user update
- [ ] Refresh user data on next access

---

## 🔐 Security Considerations

### User Info Visibility

**Current Risk:** ❌
```
Account Service exposes user emails!
Anyone with JWT can GET /users/{any_id}
```

**Solution:**
```python
@router.get("/users/{user_id}")
async def get_user(
    user_id: int, 
    current_user: Dict = Depends(get_current_user)
):
    # Option 1: Only current user can see their own details
    if user_id != current_user["id"] and not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Cannot view other users")
    
    # Option 2: Only services can see user details (service-to-service JWT)
    # Service JWT has different "scope" than user JWT
    
    return get_user_from_db(user_id)
```

---

## 📈 Performance Impact

### Without Inter-Service Calls (Current):
```
GET /projects/1/members → 1 database query → 50ms
Response: ["1", "2", "3"] (IDs only)
```

### With Inter-Service Calls (Proposed):
```
GET /projects/1/members
  ↓ Get members from DB (1 query) → 5ms
  ↓ Call Account Service for user 1 → 50ms
  ↓ Call Account Service for user 2 → 50ms
  ↓ Call Account Service for user 3 → 50ms
  ↓ Total → ~155ms
Response: Full user data for each member
```

**Solution: Batch Calls**
```python
# Instead of 3 separate calls:
# Call Account Service once with list of user IDs:
GET /users/batch?ids=1,2,3
Response:
{
  "1": {"username": "john", "email": "..."},
  "2": {"username": "sarah", "email": "..."},
  "3": {"username": "sam", "email": "..."}
}
# Total time: ~50ms instead of ~155ms
```

---

## 🎯 Recommendation

### Immediate (Before Production):

1. **Create user detail endpoints** in Account Service
   ```python
   GET /users/{user_id}
   GET /users/batch?ids=1,2,3
   ```

2. **Update responses** in Project/Group services to include user data
   ```python
   # Instead of just [{"userId": 1}]
   # Return [{"userId": 1, "username": "john", "email": "..."}]
   ```

3. **Add JWT validation** to protect user endpoints

### Phase 2 (After MVP):

4. **Implement caching** for performance
5. **Add user search** endpoint
6. **Add File Service user tracking**
7. **Event-driven updates** for profile changes

---

## Summary Table

| Service | User ID | Username | Email | Fetches Data | Problem |
|---------|---------|----------|-------|--------------|---------|
| Account | ✅ | ✅ | ✅ | - | None |
| Project | ✅ | ❌ | ❌ | ❌ No | Can't display member names |
| Group | ✅ | ❌ | ❌ | ❌ No | Can't display member names |
| File | ❌ | ❌ | ❌ | ❌ No | Can't track file ownership |

**Overall Status:** ⚠️ **Major Issue** - Services can't display user information properly
