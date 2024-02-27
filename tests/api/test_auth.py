"""Test auth API."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, patch

from aiohttp.test_utils import TestClient
import pytest

from supervisor.coresys import CoreSys

LIST_USERS_RESPONSE = [
    {
        "id": "a1d90e114a3b4da4a487fe327918dcef",
        "username": None,
        "name": "Home Assistant Content",
        "is_owner": False,
        "is_active": True,
        "local_only": False,
        "system_generated": True,
        "group_ids": ["system-read-only"],
        "credentials": [],
    },
    {
        "id": "d25a2ca897704a31ac9534b5324dc230",
        "username": None,
        "name": "Supervisor",
        "is_owner": False,
        "is_active": True,
        "local_only": False,
        "system_generated": True,
        "group_ids": ["system-admin"],
        "credentials": [],
    },
    {
        "id": "0b39e9305ba64531a8fee9ed5b86876e",
        "username": None,
        "name": "Home Assistant Cast",
        "is_owner": False,
        "is_active": True,
        "local_only": False,
        "system_generated": True,
        "group_ids": ["system-admin"],
        "credentials": [],
    },
    {
        "id": "514698a459cd4ce0b75f137a3d7df539",
        "username": "test",
        "name": "Test",
        "is_owner": True,
        "is_active": True,
        "local_only": False,
        "system_generated": False,
        "group_ids": ["system-admin"],
        "credentials": [{"type": "homeassistant"}],
    },
    {
        "id": "7d5fac79097a4eb49aff83cdf20821b0",
        "username": None,
        "name": None,
        "is_owner": False,
        "is_active": True,
        "local_only": False,
        "system_generated": False,
        "group_ids": ["system-admin"],
        "credentials": [{"type": "command_line"}],
    },
]


async def test_password_reset(
    api_client: TestClient, coresys: CoreSys, caplog: pytest.LogCaptureFixture
):
    """Test password reset api."""
    coresys.homeassistant.api.access_token = "abc123"
    # pylint: disable-next=protected-access
    coresys.homeassistant.api._access_token_expires = datetime.now(tz=UTC) + timedelta(
        days=1
    )

    mock_websession = AsyncMock()
    mock_websession.post.return_value.__aenter__.return_value.status = 200
    with patch("supervisor.coresys.aiohttp.ClientSession.post") as post:
        post.return_value.__aenter__.return_value.status = 200
        resp = await api_client.post(
            "/auth/reset", json={"username": "john", "password": "doe"}
        )
        assert resp.status == 200
        assert "Successful password reset for 'john'" in caplog.text


async def test_list_users(
    api_client: TestClient, coresys: CoreSys, ha_ws_client: AsyncMock
):
    """Test list users api."""
    ha_ws_client.async_send_command.return_value = LIST_USERS_RESPONSE
    resp = await api_client.get("/auth/list")
    assert resp.status == 200
    result = await resp.json()
    assert result["data"]["users"] == [
        {
            "username": "test",
            "name": "Test",
            "is_owner": True,
            "is_active": True,
            "local_only": False,
            "group_ids": ["system-admin"],
        },
    ]
