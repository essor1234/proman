# Group Management Service - Internal API Documentation

## Overview
The Group Management Service now exports internal REST API endpoints that allow other microservices (like project_management_service) to query and access group database information without requiring user authentication.

## Service-to-Service API Endpoints

### Base URL
```
http://localhost:8003/internal
```
(Or `http://group_service:8000/internal` from within Docker network)

---

## Endpoints

### 1. **List All Groups**
```
GET /internal/groups
```

**Query Parameters:**
- `page` (int, default=1): Page number
- `size` (int, default=50): Results per page (max 500)
- `visibility` (str, optional): Filter by visibility (public, private, invite_only)

**Response:**
```json
{
  "groups": [
    {
      "id": "uuid",
      "name": "Group Name",
      "description": "Description",
      "visibility": "private",
      "owner_id": "1",
      "member_count": 5,
      "created_at": "2025-11-21T...",
      "updated_at": "2025-11-21T..."
    }
  ],
  "total": 10,
  "page": 1,
  "size": 50,
  "pages": 1
}
```

---

### 2. **Get Specific Group**
```
GET /internal/groups/{group_id}
```

**Path Parameters:**
- `group_id` (UUID): The group ID

**Response:**
```json
{
  "id": "uuid",
  "name": "Group Name",
  "description": "Description",
  "visibility": "private",
  "owner_id": "1",
  "member_count": 5,
  "created_at": "2025-11-21T...",
  "updated_at": "2025-11-21T..."
}
```

---

### 3. **Search Groups by Name**
```
GET /internal/groups/search
```

**Query Parameters:**
- `name` (str, required): Search term (partial match)
- `limit` (int, default=20): Max results (max 100)

**Response:**
```json
{
  "search_term": "test",
  "result_count": 2,
  "groups": [...]  // Same as list groups response
}
```

---

### 4. **Get Group Members**
```
GET /internal/groups/{group_id}/members
```

**Response:**
```json
{
  "group_id": "uuid",
  "group_name": "Group Name",
  "member_count": 3,
  "members": [
    {
      "user_id": "1",
      "role": "owner",
      "status": "ACTIVE",
      "joined_at": "2025-11-14T12:40:35.505598"
    }
  ]
}
```

---

### 5. **Get Member IDs Only**
```
GET /internal/groups/{group_id}/members-ids
```

**Response:**
```json
{
  "group_id": "uuid",
  "member_ids": ["1", "2", "3"]
}
```

---

### 6. **Check if User is Member**
```
GET /internal/groups/{group_id}/check-member/{user_id}
```

**Response:**
```json
{
  "group_id": "uuid",
  "user_id": "1",
  "is_member": true,
  "role": "member",
  "status": "ACTIVE"
}
```

---

### 7. **Get Groups for User**
```
GET /internal/users/{user_id}/groups
```

**Response:**
```json
{
  "user_id": "1",
  "group_count": 3,
  "groups": [
    {
      "id": "uuid",
      "name": "Group Name",
      "description": "Description",
      "visibility": "private",
      "owner_id": "1",
      "member_count": 5,
      "user_role": "owner",
      "created_at": "2025-11-21T...",
      "updated_at": "2025-11-21T..."
    }
  ]
}
```

---

### 8. **Get Statistics**
```
GET /internal/groups/stats
```

**Response:**
```json
{
  "total_groups": 10,
  "public_groups": 4,
  "private_groups": 6,
  "total_memberships": 12,
  "avg_group_size": 1.2
}
```

---

## Usage Example (from project_management_service)

```python
import requests

# Get all groups with their member counts
response = requests.get('http://group_service:8000/internal/groups?page=1&size=50')
groups_data = response.json()

# Check if a user is in a group
response = requests.get('http://group_service:8000/internal/groups/{group_id}/check-member/{user_id}')
membership = response.json()

if membership['is_member']:
    print(f"User is {membership['role']}")

# Get all groups for a specific user
response = requests.get('http://group_service:8000/internal/users/{user_id}/groups')
user_groups = response.json()

# Search for groups
response = requests.get('http://group_service:8000/internal/groups/search?name=project&limit=10')
search_results = response.json()

# Get system statistics
response = requests.get('http://group_service:8000/internal/groups/stats')
stats = response.json()
print(f"Total groups: {stats['total_groups']}")
```

---

## Security Notes

⚠️ **Important**: These endpoints are currently designed for internal service-to-service communication within the Docker network. 

**For production deployment**, implement one of:
1. **API Key Authentication**: Add `X-API-Key` header validation
2. **mTLS (Mutual TLS)**: Secure service-to-service communication
3. **Network Isolation**: Restrict access to internal Docker network only
4. **Rate Limiting**: Implement to prevent abuse

Example production implementation:
```python
@router.get("/internal/groups")
async def list_all_groups(..., api_key: str = Header(...)):
    if api_key != os.getenv("INTERNAL_API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API key")
    # ... rest of implementation
```

---

## Error Responses

All endpoints return standard HTTP error codes:

- **200 OK**: Successful request
- **404 Not Found**: Resource doesn't exist
- **422 Unprocessable Entity**: Invalid query parameters
- **500 Internal Server Error**: Server error

Example error response:
```json
{
  "detail": "Group not found"
}
```

---

## Performance Considerations

- All endpoints support pagination for large datasets
- Member lists are retrieved efficiently using indexed queries
- Statistics endpoint caches calculations in production
- Search uses database-level string matching (case-insensitive)

---

## Docker Network Usage

From within the Docker network, use:
```
http://group_service:8000/internal
```

From host machine:
```
http://localhost:8003/internal
```
