# Quick Reference - Group Service API

## 🔗 Quick Links
- **Host**: http://localhost:8003
- **Docker**: http://group_service:8000
- **Swagger UI**: http://localhost:8003/docs

---

## 👥 User-Facing Endpoints (Require JWT)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/groups` | List user's groups (paginated) |
| POST | `/groups` | Create new group |
| GET | `/groups/{id}` | Get group details |
| PUT | `/groups/{id}` | Update group |
| DELETE | `/groups/{id}` | Delete group |
| GET | `/groups/{id}/members` | List members + user profiles |
| POST | `/groups/{id}/members` | Add member |
| DELETE | `/groups/{id}/members/{user_id}` | Remove member |

---

## 🔧 Internal API Endpoints (No Auth)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/internal/groups` | List all groups |
| GET | `/internal/groups/{id}` | Get group by ID |
| GET | `/internal/groups/search?name=...` | Search groups |
| GET | `/internal/groups/stats` | Get statistics |
| GET | `/internal/groups/{id}/members` | Get group members |
| GET | `/internal/groups/{id}/members-ids` | Get member IDs |
| GET | `/internal/groups/{id}/check-member/{user_id}` | Check membership |
| GET | `/internal/users/{user_id}/groups` | Get user's groups |

---

## 🧪 Test Commands

```bash
# List groups
curl http://localhost:8003/internal/groups

# Search groups
curl http://localhost:8003/internal/groups/search?name=test

# Get statistics
curl http://localhost:8003/internal/groups/stats

# Check if user is member
curl http://localhost:8003/internal/groups/{group_id}/check-member/{user_id}

# Get user's groups
curl http://localhost:8003/internal/users/1/groups
```

---

## 🐳 Docker Commands

```bash
# View logs
docker-compose logs group_service

# Restart service
docker-compose restart group_service

# Stop service
docker-compose stop group_service

# Start service
docker-compose up -d group_service
```

---

## 📊 Database Schema

**Groups Table:**
- id (UUID)
- name (String)
- description (String)
- visibility (String: public, private, invite_only)
- owner_id (String)
- created_at, updated_at (DateTime)

**Memberships Table:**
- id (UUID)
- group_id (String)
- user_id (String)
- role (String: owner, admin, member)
- status (String: ACTIVE, PENDING, REMOVED)
- joined_at, updated_at (DateTime)

---

## 🔐 JWT Token Format

```python
# Token payload should contain:
{
  "sub": "1",                    # User ID
  "username": "johndoe",
  "email": "john@example.com",
  "exp": 1763...                 # Expiration time
}
```

**Secret Key**: `your-secret-key-change-in-production-and-match-auth-service`  
**Algorithm**: `HS256`

---

## 🌍 Service URLs (Docker Network)

```
Account Service:  http://account_service:8000
Group Service:    http://group_service:8000
```

---

## 📝 Common Response Formats

### Success Response (200)
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

### Error Response (400/404/500)
```json
{
  "detail": "Group not found"
}
```

---

## 🎯 Usage Examples

### Python Client
```python
import requests

# Internal API - No auth needed
resp = requests.get('http://group_service:8000/internal/groups?page=1&size=50')
groups = resp.json()

# Check membership
resp = requests.get(f'http://group_service:8000/internal/groups/{group_id}/check-member/{user_id}')
is_member = resp.json()['is_member']
```

### JavaScript/Node.js
```javascript
// Fetch all groups
const response = await fetch('http://localhost:8003/internal/groups');
const groups = await response.json();

// Search groups
const search = await fetch('http://localhost:8003/internal/groups/search?name=project');
const results = await search.json();
```

---

## ⚙️ Configuration Files

**Main Config** (`app/core/config.py`):
```python
ACCOUNT_SERVICE_URL = "http://account_service:8000"
JWT_SECRET_KEY = "your-secret-key-change-in-production-and-match-auth-service"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
```

---

## 📚 Documentation

- See `INTERNAL_API_DOCUMENTATION.md` for detailed API reference
- See `GROUP_SERVICE_SUMMARY.md` for complete implementation overview
- Visit `/docs` for interactive Swagger UI

---

## ✅ Status Check

Service is healthy if:
1. ✅ All containers running: `docker-compose ps`
2. ✅ Can access Swagger: http://localhost:8003/docs
3. ✅ Can query groups: `curl http://localhost:8003/internal/groups`
4. ✅ DB initialized: Tables created automatically on startup

---

**Last Updated**: November 21, 2025
