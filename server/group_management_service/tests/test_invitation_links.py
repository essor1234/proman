import pytest
from fastapi.testclient import TestClient
from jose import jwt
from datetime import datetime, timedelta

from app.main import app  # Import your FastAPI app instance

client = TestClient(app)

# Use the same secret as defined in the app's config for decoding
SECRET_KEY = "mySecretKey"
ALGORITHM = "HS256"

@pytest.fixture(scope="module")
def auth_headers():
    # The current security implementation is loose, 
    # it just needs a token that can be cast to an int.
    return {"Authorization": "Bearer 1"}

def test_generate_invite_link_success(auth_headers):
    """
    Test successful generation of an invite link.
    """
    group_id = 12345
    
    # Act
    response = client.post(
        f"/groups/{group_id}/generate-invite-link",
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == 201
    
    data = response.json()
    assert "inviteLink" in data
    assert "token" in data
    
    # Verify the link format
    assert data["inviteLink"].startswith("https://example.com/invite?token=")
    assert data["inviteLink"].endswith(data["token"])
    
    # Decode and verify the JWT payload
    token = data["token"]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        assert payload["groupId"] == group_id
        
        # Check that the expiration is in the future
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
        assert exp_datetime > datetime.utcnow()
        
        # Check that it expires within 24 hours (with a small buffer for execution time)
        expected_exp = datetime.utcnow() + timedelta(hours=24)
        assert exp_datetime < expected_exp + timedelta(seconds=10)

    except jwt.JWTError as e:
        pytest.fail(f"JWT decoding failed: {e}")

def test_generate_invite_link_unauthorized():
    """
    Test endpoint access without authorization.
    """
    group_id = 12345
    
    # Act
    response = client.post(f"/groups/{group_id}/generate-invite-link") # No headers
    
    # Assert
    # Based on security.py, it should raise a 401 if no token is present
    assert response.status_code == 401
    assert response.json() == {"detail": "Missing token"}
