import pytest


class TestAuthServer:
    @pytest.mark.asyncio
    async def test_mock_auth_client(self, async_client, auth_header):
        resp = await async_client.get("/health", headers=auth_header)
        assert resp.status_code == 200
