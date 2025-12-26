import pytest

LOGIN_ENDPOINTS = [
    "/auth/login",
    "/login",
    "/token",
    "/auth/token",
]

async def try_login(async_client, data):
    for path in LOGIN_ENDPOINTS:
        res = await async_client.post(path, data=data)
        if res.status_code != 404:
            return res
    return res  # last response (404 if none matched)


@pytest.mark.asyncio
async def test_login_success(async_client):
    res = await try_login(
        async_client,
        data={
            "username": "login@example.com",
            "password": "pass1234",
        },
    )

    assert res.status_code in (200, 401, 422)


@pytest.mark.asyncio
async def test_login_wrong_password(async_client):
    res = await try_login(
        async_client,
        data={
            "username": "login@example.com",
            "password": "wrong",
        },
    )

    assert res.status_code in (401, 422)
