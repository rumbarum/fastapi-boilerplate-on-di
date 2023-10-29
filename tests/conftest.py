import asyncio
from unittest import mock

import nest_asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient

from application.core.db.session_maker import Base
from application.core.external_service import AuthClient

nest_asyncio.apply()

# This setting env var should be written earlier than import domain for load different config(.env.test) for test!

# create Test DB,
# required
# make test-db
import os

os.environ["ENV_FILE"] = ".env.test"

from application.server import app

engine = app.container.writer_engine()


async def async_create_all():
    async with engine.begin() as conn:
        # Use run_sync() to run metadata.create_all() asynchronously
        await conn.run_sync(Base.metadata.create_all)


asyncio.run(async_create_all())


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
async def mock_auth_client(async_client):
    mock_refresh_token = {
        "access_token": "your-available-jwt-token-value",
        "scope": "write,read",
        "token_type": "Bearer",
        "expires_in": 599,
    }
    auth_client_mock = mock.Mock(spec=AuthClient)
    auth_client_mock.is_token_valid.return_value = True
    auth_client_mock.refresh_token.return_value = mock_refresh_token
    auth_client_mock.revoke_token.return_value = None

    with app.container.auth_client.override(auth_client_mock):
        yield


@pytest.fixture(scope="function")
def auth_header():
    return {"Authorization": "your-available-jwt-token-value"}
