import asyncio
import sys
import os
import pytest
from httpx import AsyncClient

# Ensure project root is on sys.path so `server` package is importable
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Create an alias so imports written as `import app.*` inside the service
# resolve to the same modules as `server.group_management_service.app.*` and
# avoid loading the package twice under different names.
import importlib
try:
    app_pkg = importlib.import_module("server.group_management_service.app")
    sys.modules["app"] = app_pkg
    try:
        core_pkg = importlib.import_module("server.group_management_service.app.core")
        sys.modules["app.core"] = core_pkg
    except Exception:
        pass
except Exception:
    # if the package isn't importable yet that's fine; imports below will handle it
    pass

# Replace this with the real import path of your FastAPI app
from server.group_management_service.app.main import app  # <-- change if needed


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
