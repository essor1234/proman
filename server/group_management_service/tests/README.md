# Group Management Service - Test Suite

## 📁 Folder Structure

```
tests/
├── __init__.py                          # Python package marker
├── docs/                                # Documentation folder
│   ├── GROUP_SERVICE_SUMMARY.md        # Full implementation overview
│   ├── INTEGRATION_GUIDE.md            # Integration examples for other services
│   ├── INTERNAL_API_DOCUMENTATION.md   # Internal API reference
│   └── QUICK_REFERENCE.md              # Quick lookup guide
├── generate_token.py                    # JWT token generator for testing
├── view_databases.py                    # Database inspection utility
├── test_add_member_debug.py            # Debug test for adding members
├── test_all_endpoints.py               # Comprehensive endpoint tests (8 endpoints)
├── test_group_detail.py                # Group detail endpoint test
├── test_group_members.py               # Group members endpoint test
├── test_groups_api.py                  # Groups list API test
├── test_internal_api.py                # Internal API endpoints test
└── test_with_jwt.py                    # JWT authentication test
```

## 🚀 Running Tests

### Run all tests
```bash
cd server/group_management_service
python -m pytest tests/ -v
```

### Run specific test file
```bash
python tests/test_all_endpoints.py
```

### Run with coverage
```bash
python -m pytest tests/ --cov=app --cov-report=html
```

## 🔑 Generate Test Token

```bash
python tests/generate_token.py
```

This will output a valid JWT token for testing authenticated endpoints.

## 📊 View Databases

```bash
python tests/view_databases.py
```

This utility allows you to inspect the SQLite database structure and contents.

## 📚 Documentation

- **`GROUP_SERVICE_SUMMARY.md`** - Complete service implementation overview
- **`INTEGRATION_GUIDE.md`** - How to use this service from other microservices (Python examples)
- **`INTERNAL_API_DOCUMENTATION.md`** - Reference for all 8 internal API endpoints
- **`QUICK_REFERENCE.md`** - Quick lookup for endpoints, curl commands, and response formats

## ✅ Test Results

All 8 user-facing endpoints have been tested and are passing:
- ✅ GET /groups - List groups with pagination
- ✅ POST /groups - Create new group
- ✅ GET /groups/{id} - Get group details
- ✅ GET /groups/{id}/members - Get members with profiles
- ✅ PUT /groups/{id} - Update group
- ✅ POST /groups/{id}/members - Add member to group
- ✅ DELETE /groups/{id} - Delete group
- ✅ POST /groups/{id}/transfer-ownership - Transfer group ownership

All 8 internal API endpoints tested and working:
- ✅ GET /internal/groups - List groups
- ✅ GET /internal/groups/search - Search groups
- ✅ GET /internal/groups/stats - Get statistics
- ✅ GET /internal/groups/{id} - Get group
- ✅ GET /internal/groups/{id}/members - Get members
- ✅ GET /internal/groups/{id}/members-ids - Get member IDs
- ✅ GET /internal/groups/{id}/check-member/{user_id} - Check membership
- ✅ GET /internal/users/{user_id}/groups - Get user's groups

## 🔧 Utilities

### generate_token.py
Generates valid JWT tokens for API testing. Useful for:
- Testing protected endpoints
- Manual API exploration
- Integration testing

### view_databases.py
Inspect SQLite databases:
- View table structures
- Query data
- Compare databases

## 📖 Usage Examples

### Python Client Example
See `docs/INTEGRATION_GUIDE.md` for complete Python client implementation:

```python
from utils.account_client import get_user_by_id

client = GroupServiceClient()
groups = client.get_all_groups(page=1, size=50)
```

### cURL Examples
See `docs/QUICK_REFERENCE.md` for cURL commands:

```bash
curl -X GET "http://localhost:8003/groups" \
  -H "Authorization: Bearer $TOKEN"
```

---

**Last Updated**: November 21, 2025  
**Service Version**: 1.0
