import pytest

@pytest.mark.asyncio
async def test_root_alive(async_client):
    r = await async_client.get("/")
    assert r.status_code == 200
