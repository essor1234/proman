import sys
import os
import importlib
import pytest_asyncio
from httpx import AsyncClient
from httpx import ASGITransport

# Ensure project root is on sys.path so `server` package is importable
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Alias app imports
try:
    app_pkg = importlib.import_module("server.account_management_service.app")
    sys.modules["app"] = app_pkg
    try:
        core_pkg = importlib.import_module("server.account_management_service.app.core")
        sys.modules["app.core"] = core_pkg
    except Exception:
        pass
except Exception:
    pass

from server.account_management_service.app.main import app


@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as ac:
        yield ac
