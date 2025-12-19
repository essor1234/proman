"""
Comprehensive unit tests for Account Service endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, select
from sqlmodel.pool import StaticPool

from app.main import app
from app.core.db import get_db
from app.models.user import User
from app.core.security import hash_password_secure

# Test database setup
@pytest.fixture(name="session")
def session_fixture():
    """Create test database session"""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    from app.core.db import SQLModel
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create test client with test database"""
    def get_session_override():
        return session

    app.dependency_overrides[get_db] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestAuth:
    """Test authentication endpoints"""
    
    def test_register_user(self, client: TestClient):
        """Test user registration"""
        response = client.post(
            "/auth/register",
            data={
                "username": "testuser",
                "email": "test@example.com",
                "password": "TestPass123!",
                "full_name": "Test User"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["full_name"] == "Test User"
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "hashed_password" not in data  # Should not expose password
    
    def test_register_duplicate_username(self, client: TestClient):
        """Test registration with duplicate username"""
        # Register first user
        client.post(
            "/auth/register",
            data={
                "username": "testuser",
                "email": "test1@example.com",
                "password": "TestPass123!"
            }
        )
        # Try to register with same username
        response = client.post(
            "/auth/register",
            data={
                "username": "testuser",
                "email": "test2@example.com",
                "password": "TestPass123!"
            }
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
    
    def test_login_success(self, client: TestClient):
        """Test successful login"""
        # Register
        client.post(
            "/auth/register",
            data={
                "username": "testuser",
                "email": "test@example.com",
                "password": "TestPass123!"
            }
        )
        # Login
        response = client.post(
            "/auth/login",
            data={
                "username": "testuser",
                "password": "TestPass123!"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert "access_token" in data
        assert "hashed_password" not in data
    
    def test_login_wrong_password(self, client: TestClient):
        """Test login with wrong password"""
        # Register
        client.post(
            "/auth/register",
            data={
                "username": "testuser",
                "email": "test@example.com",
                "password": "TestPass123!"
            }
        )
        # Login with wrong password
        response = client.post(
            "/auth/login",
            data={
                "username": "testuser",
                "password": "WrongPass123!"
            }
        )
        assert response.status_code == 401
        assert "Invalid password" in response.json()["detail"]
    
    def test_login_user_not_found(self, client: TestClient):
        """Test login with non-existent user"""
        response = client.post(
            "/auth/login",
            data={
                "username": "nonexistent",
                "password": "TestPass123!"
            }
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestUserEndpoints:
    """Test user data endpoints"""
    
    def test_get_user_authenticated(self, client: TestClient):
        """Test getting user details when authenticated"""
        # Register
        reg_response = client.post(
            "/auth/register",
            data={
                "username": "alice",
                "email": "alice@example.com",
                "password": "TestPass123!",
                "full_name": "Alice"
            }
        )
        token = reg_response.json()["access_token"]
        
        # Get user
        response = client.get(
            "/auth/users/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["username"] == "alice"
        assert data["email"] == "alice@example.com"
        assert data["full_name"] == "Alice"
        assert "hashed_password" not in data
    
    def test_get_user_unauthenticated(self, client: TestClient):
        """Test getting user details without authentication"""
        response = client.get("/auth/users/1")
        assert response.status_code == 403
        assert "Not authenticated" in response.json()["detail"]
    
    def test_get_user_not_found(self, client: TestClient):
        """Test getting non-existent user"""
        # Register to get token
        reg_response = client.post(
            "/auth/register",
            data={
                "username": "alice",
                "email": "alice@example.com",
                "password": "TestPass123!"
            }
        )
        token = reg_response.json()["access_token"]
        
        # Try to get non-existent user
        response = client.get(
            "/auth/users/999",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_batch_users(self, client: TestClient):
        """Test batch user fetch"""
        # Register multiple users
        users = ["alice", "bob", "charlie"]
        token = None
        for user in users:
            reg_response = client.post(
                "/auth/register",
                data={
                    "username": user,
                    "email": f"{user}@example.com",
                    "password": "TestPass123!"
                }
            )
            token = reg_response.json()["access_token"]
        
        # Fetch batch
        response = client.get(
            "/auth/users/batch?ids=1,2,3",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "1" in data
        assert "2" in data
        assert "3" in data
        assert data["1"]["username"] == "alice"
        assert data["2"]["username"] == "bob"
    
    def test_search_users(self, client: TestClient):
        """Test user search"""
        # Register users
        client.post(
            "/auth/register",
            data={
                "username": "alice",
                "email": "alice@example.com",
                "password": "TestPass123!"
            }
        )
        reg_response = client.post(
            "/auth/register",
            data={
                "username": "bob",
                "email": "bob@example.com",
                "password": "TestPass123!"
            }
        )
        token = reg_response.json()["access_token"]
        
        # Search
        response = client.get(
            "/auth/users/search?q=alice",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["count"] >= 1
        assert any(u["username"] == "alice" for u in data["users"])
    
    def test_search_query_too_short(self, client: TestClient):
        """Test search with query too short"""
        client.post(
            "/auth/register",
            data={
                "username": "alice",
                "email": "alice@example.com",
                "password": "TestPass123!"
            }
        )
        reg_response = client.post(
            "/auth/register",
            data={
                "username": "bob",
                "email": "bob@example.com",
                "password": "TestPass123!"
            }
        )
        token = reg_response.json()["access_token"]
        
        # Search with short query
        response = client.get(
            "/auth/users/search?q=a",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 400
        assert "at least 2 characters" in response.json()["detail"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
