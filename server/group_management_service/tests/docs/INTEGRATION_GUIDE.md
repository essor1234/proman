# Integration Guide: Using Group Service from Project Management Service

This guide shows how `project_management_service` can integrate with the `group_management_service` using the internal API.

---

## 📦 Installation

```bash
pip install httpx requests
```

---

## 🔗 Service URLs

```python
# From within Docker network
GROUP_SERVICE_URL = "http://group_service:8000"

# From host machine (development)
GROUP_SERVICE_URL = "http://localhost:8003"
```

---

## 🛠️ Python Client Implementation

### Basic Setup

```python
import httpx
from typing import Optional, List

class GroupServiceClient:
    def __init__(self, base_url: str = "http://group_service:8000"):
        self.base_url = base_url
        self.client = httpx.Client()
    
    def _request(self, method: str, endpoint: str, **kwargs):
        url = f"{self.base_url}/internal{endpoint}"
        response = self.client.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()

# Initialize client
group_client = GroupServiceClient()
```

### Get All Groups

```python
def get_all_groups(page: int = 1, size: int = 50) -> dict:
    """Retrieve all groups with pagination"""
    return group_client._request(
        "GET",
        "/groups",
        params={"page": page, "size": size}
    )

# Usage
groups_data = get_all_groups(page=1, size=100)
print(f"Total groups: {groups_data['total']}")
for group in groups_data['groups']:
    print(f"  - {group['name']} ({group['member_count']} members)")
```

### Get Specific Group

```python
def get_group(group_id: str) -> dict:
    """Get single group details"""
    return group_client._request("GET", f"/groups/{group_id}")

# Usage
group = get_group("63eb1a38-6f3b-470a-ba52-7d9db3a061b9")
print(f"Group: {group['name']}")
print(f"Owner: {group['owner_id']}")
print(f"Members: {group['member_count']}")
```

### Search Groups

```python
def search_groups(name: str, limit: int = 20) -> dict:
    """Search for groups by name"""
    return group_client._request(
        "GET",
        "/groups/search",
        params={"name": name, "limit": limit}
    )

# Usage
results = search_groups("engineering")
for group in results['groups']:
    print(f"Found: {group['name']}")
```

### Get Group Members

```python
def get_group_members(group_id: str) -> dict:
    """Get list of members in a group"""
    return group_client._request("GET", f"/groups/{group_id}/members")

# Usage
members_data = get_group_members("63eb1a38-6f3b-470a-ba52-7d9db3a061b9")
for member in members_data['members']:
    print(f"  - {member['user_id']} ({member['role']})")
```

### Quick Member ID Lookup

```python
def get_member_ids(group_id: str) -> List[str]:
    """Get just the list of member IDs (fast)"""
    data = group_client._request("GET", f"/groups/{group_id}/members-ids")
    return data['member_ids']

# Usage - efficient for permission checks
user_id = "42"
members = set(get_member_ids(group_id))
if user_id in members:
    print("User is in the group")
```

### Check Membership

```python
def is_user_member(group_id: str, user_id: str) -> bool:
    """Quick check if user is member of group"""
    data = group_client._request(
        "GET",
        f"/groups/{group_id}/check-member/{user_id}"
    )
    return data['is_member']

# Usage
if is_user_member(group_id, "42"):
    print("User has access")
```

### Get User's Groups

```python
def get_user_groups(user_id: str) -> dict:
    """Get all groups a user belongs to"""
    return group_client._request("GET", f"/users/{user_id}/groups")

# Usage
user_groups = get_user_groups("42")
print(f"User is in {user_groups['group_count']} groups:")
for group in user_groups['groups']:
    print(f"  - {group['name']} (role: {group['user_role']})")
```

### Get Statistics

```python
def get_stats() -> dict:
    """Get system-wide group statistics"""
    return group_client._request("GET", "/groups/stats")

# Usage
stats = get_stats()
print(f"Total groups: {stats['total_groups']}")
print(f"Public groups: {stats['public_groups']}")
print(f"Average group size: {stats['avg_group_size']}")
```

---

## 📋 Complete Integration Example

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import httpx

app = FastAPI()

class GroupServiceClient:
    def __init__(self, base_url: str = "http://group_service:8000"):
        self.base_url = base_url
    
    def _request(self, method: str, endpoint: str, **kwargs):
        with httpx.Client() as client:
            url = f"{self.base_url}/internal{endpoint}"
            response = client.request(method, url, **kwargs, timeout=5.0)
            response.raise_for_status()
            return response.json()
    
    def get_all_groups(self, page: int = 1):
        return self._request("GET", "/groups", params={"page": page})
    
    def search_groups(self, name: str):
        return self._request("GET", "/groups/search", params={"name": name})
    
    def get_user_groups(self, user_id: str):
        return self._request("GET", f"/users/{user_id}/groups")
    
    def is_member(self, group_id: str, user_id: str) -> bool:
        data = self._request("GET", f"/groups/{group_id}/check-member/{user_id}")
        return data['is_member']

# Initialize client
group_client = GroupServiceClient()

# Use in endpoints
@app.get("/projects")
async def list_projects(user_id: str):
    """List projects user can access"""
    try:
        user_groups = group_client.get_user_groups(user_id)
        return {
            "groups": user_groups['groups'],
            "project_count": len(user_groups['groups'])
        }
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail="Group service unavailable")

@app.get("/projects/{project_id}/collaborators")
async def get_collaborators(project_id: str):
    """Get all users in a project (using group membership)"""
    try:
        members = group_client._request("GET", f"/groups/{project_id}/members-ids")
        return {"collaborators": members['member_ids']}
    except httpx.HTTPError:
        raise HTTPException(status_code=502, detail="Group service unavailable")

@app.post("/projects/{project_id}/add-member/{user_id}")
async def add_member_to_project(project_id: str, user_id: str):
    """Add user to project (if user is in group)"""
    try:
        if not group_client.is_member(project_id, user_id):
            raise HTTPException(status_code=403, detail="User not in group")
        # Add to project...
        return {"status": "added"}
    except httpx.HTTPError:
        raise HTTPException(status_code=502, detail="Group service unavailable")
```

---

## 🛡️ Error Handling

```python
import httpx
from fastapi import HTTPException

def safe_group_call(func):
    """Decorator to handle group service errors"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except httpx.HTTPError as e:
            if isinstance(e, httpx.ConnectError):
                raise HTTPException(status_code=502, detail="Group service unavailable")
            elif isinstance(e, httpx.HTTPStatusError):
                if e.response.status_code == 404:
                    raise HTTPException(status_code=404, detail="Group not found")
                else:
                    raise HTTPException(status_code=500, detail="Group service error")
            else:
                raise HTTPException(status_code=500, detail="Internal error")
    return wrapper

@safe_group_call
def get_group_data(group_id: str):
    return group_client._request("GET", f"/groups/{group_id}")
```

---

## 🔄 Caching Strategy

```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedGroupClient:
    def __init__(self, base_url: str = "http://group_service:8000", ttl: int = 300):
        self.base_url = base_url
        self.ttl = ttl
        self.cache = {}
    
    def _request(self, method: str, endpoint: str, **kwargs):
        # Check cache
        cache_key = (method, endpoint, str(kwargs))
        if cache_key in self.cache:
            data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < timedelta(seconds=self.ttl):
                return data
        
        # Make request
        with httpx.Client() as client:
            url = f"{self.base_url}/internal{endpoint}"
            response = client.request(method, url, **kwargs, timeout=5.0)
            response.raise_for_status()
            result = response.json()
        
        # Cache result
        self.cache[cache_key] = (result, datetime.now())
        return result
    
    def clear_cache(self):
        self.cache.clear()

# Usage
cached_client = CachedGroupClient(ttl=600)  # 10 minute cache
```

---

## 🧪 Testing

```python
import pytest
from unittest.mock import patch, MagicMock

@patch('httpx.Client')
def test_get_all_groups(mock_client):
    # Mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "groups": [{"id": "123", "name": "Test"}],
        "total": 1
    }
    mock_client.return_value.__enter__.return_value.request.return_value = mock_response
    
    # Test
    client = GroupServiceClient()
    result = client.get_all_groups()
    
    assert result['total'] == 1
    assert len(result['groups']) == 1

@patch('httpx.Client')
def test_group_not_found(mock_client):
    # Mock 404 response
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError("404", request=None, response=None)
    mock_client.return_value.__enter__.return_value.request.return_value = mock_response
    
    # Test
    client = GroupServiceClient()
    with pytest.raises(httpx.HTTPStatusError):
        client.get_group("invalid-id")
```

---

## 🚀 Production Deployment

### Docker Compose Integration

```yaml
version: '3.8'
services:
  project_management_service:
    build: ./project_management_service
    ports:
      - "8004:8000"
    environment:
      GROUP_SERVICE_URL: "http://group_service:8000"
    depends_on:
      - group_service
  
  group_service:
    build: ./group_management_service
    ports:
      - "8003:8000"
    environment:
      ACCOUNT_SERVICE_URL: "http://account_service:8000"
```

### Environment Configuration

```python
import os

GROUP_SERVICE_URL = os.getenv(
    "GROUP_SERVICE_URL",
    "http://group_service:8000"
)

GROUP_SERVICE_TIMEOUT = int(os.getenv("GROUP_SERVICE_TIMEOUT", "5"))

GROUP_SERVICE_RETRIES = int(os.getenv("GROUP_SERVICE_RETRIES", "3"))
```

---

## 📚 Additional Resources

- **API Documentation**: See `/docs` endpoint on group_service
- **Internal API Reference**: `INTERNAL_API_DOCUMENTATION.md`
- **Full Implementation**: `GROUP_SERVICE_SUMMARY.md`

---

**Version**: 1.0  
**Last Updated**: November 21, 2025
