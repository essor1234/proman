import pytest
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


def test_user_model_validation():
    u = UserCreate(email="valid@example.com", password="secret")
    assert u.email == "valid@example.com"

    with pytest.raises(ValueError):
        UserCreate(email="not-an-email", password="pw")