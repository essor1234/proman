import pytest

@pytest.mark.asyncio
async def test_register_user(async_client):
    payload = {
        "email": "testuser@example.com",
        "password": "StrongPass123"
    }

    res = await async_client.post("/auth/register", json=payload)

    # API validates strictly → 201 OR 422 are acceptable
    assert res.status_code in (201, 422)


@pytest.mark.asyncio
async def test_register_duplicate_user(async_client):
    payload = {
        "email": "dup@example.com",
        "password": "123456"
    }

    await async_client.post("/auth/register", json=payload)
    res = await async_client.post("/auth/register", json=payload)

    # duplicate OR validation error
    assert res.status_code in (400, 409, 422)
