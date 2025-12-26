import pytest
from fastapi.testclient import TestClient
from app.main import app, get_current_user  # Import the actual dependency; adjust name/path if needed
import jwt
from datetime import datetime, timedelta
import time
import os
from typing import Dict

# Load from env
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-and-match-auth-service")
ALGORITHM = "HS256"

# Mock user to return (matches the test token's payload)
mock_user = {
    "id": "1",
    "username": "testuser",
    "email": "test@example.com"
}

def mock_get_current_user() -> Dict:
    """Mock dependency to bypass JWT validation in tests"""
    return mock_user

# Override the dependency globally for the test app
app.dependency_overrides[get_current_user] = mock_get_current_user

client = TestClient(app)

def create_test_token(user_id="1", username="testuser", email="test@example.com"):
    """Create a JWT token for testing (optional now, since auth is mocked)"""
    payload = {
        "sub": str(user_id),
        "username": username,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

@pytest.fixture(scope="class")
def auth_headers():
    """Fixture to provide authorization headers (token still sent, but validation mocked)"""
    token = create_test_token()
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="class")
def created_group_id(auth_headers):
    """Fixture to create a group and yield its ID, then delete it"""
    group_data = {
        "name": f"Test Group {time.time()}",
        "description": "This is a test group",
        "visibility": "private"
    }
    response = client.post("/groups", json=group_data, headers=auth_headers)
    if response.status_code in [200, 201]:
        group_id = response.json()["id"]
        yield group_id
        # Cleanup
        client.delete(f"/groups/{group_id}", headers=auth_headers)
    else:
        yield None

class TestGroupManagementAutomation:
    """Automated tests for Group Management Service"""

    def test_get_groups(self, auth_headers):
        """Test GET /groups - List all groups"""
        response = client.get("/groups", headers=auth_headers)
        assert response.status_code in [200, 404]  # 404 if no groups exist
        if response.status_code == 200:
            data = response.json()
            assert "groups" in data
            assert "total" in data
            assert isinstance(data["groups"], list)

    def test_create_group(self, auth_headers):
        """Test POST /groups - Create a new group"""
        group_data = {
            "name": f"Test Group {time.time()}",
            "description": "This is a test group",
            "visibility": "private"
        }
        response = client.post("/groups", json=group_data, headers=auth_headers)
        assert response.status_code in [200, 201]
        if response.status_code in [200, 201]:
            created_group = response.json()
            assert "id" in created_group
            assert created_group["name"] == group_data["name"]
            # Cleanup (optional here since fixture can handle)
            client.delete(f"/groups/{created_group['id']}", headers=auth_headers)

    def test_get_group_detail(self, auth_headers, created_group_id):
        """Test GET /groups/{id} - Get specific group"""
        if not created_group_id:
            pytest.skip("Group creation failed")
        response = client.get(f"/groups/{created_group_id}", headers=auth_headers)
        assert response.status_code == 200
        group = response.json()
        assert group["id"] == created_group_id
        assert "name" in group
        assert "owner_id" in group

    def test_get_group_members(self, auth_headers, created_group_id):
        """Test GET /groups/{id}/members - Get group members"""
        if not created_group_id:
            pytest.skip("Group creation failed")
        response = client.get(f"/groups/{created_group_id}/members", headers=auth_headers)
        assert response.status_code == 200
        group_data = response.json()
        assert "members" in group_data
        assert "member_count" in group_data
        assert isinstance(group_data["members"], list)

    def test_update_group(self, auth_headers, created_group_id):
        """Test PUT /groups/{id} - Update group"""
        if not created_group_id:
            pytest.skip("Group creation failed")
        update_data = {
            "name": f"Updated Group {time.time()}",
            "description": "Updated description",
            "visibility": "public"
        }
        response = client.put(f"/groups/{created_group_id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        updated_group = response.json()
        assert updated_group["name"] == update_data["name"]
        assert updated_group["visibility"] == update_data["visibility"]

    def test_add_member_to_group(self, auth_headers, created_group_id):
        """Test POST /groups/{id}/members - Add member to group"""
        if not created_group_id:
            pytest.skip("Group creation failed")
        member_data = {
            "user_id": "2"  # Add user 2
        }
        response = client.post(f"/groups/{created_group_id}/members", json=member_data, headers=auth_headers)
        assert response.status_code in [200, 201, 400]  # 400 if user already member

    def test_pagination(self, auth_headers):
        """Test GET /groups with pagination"""
        response = client.get("/groups?page=1&size=2", headers=auth_headers)
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "page" in data
            assert "size" in data
            assert "total" in data
            assert "has_more" in data
            assert len(data["groups"]) <= data["size"]

    def test_unauthorized_access(self):
        """Test accessing endpoints without authorization"""
        response = client.get("/groups")
        assert response.status_code == 401

    def test_invalid_token(self):
        """Test accessing endpoints with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/groups", headers=headers)
        assert response.status_code == 401

# Clean up overrides after tests (good practice)
@pytest.fixture(scope="session", autouse=True)
def cleanup_overrides():
    yield
    app.dependency_overrides = {}

if __name__ == "__main__":
    pytest.main([__file__, "-v"])