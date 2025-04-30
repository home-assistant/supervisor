"""Test auth API."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from aiohttp.test_utils import TestClient
import pytest

from supervisor.addons.addon import Addon
from supervisor.coresys import CoreSys

from tests.common import MockResponse
from tests.const import TEST_ADDON_SLUG

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


@pytest.fixture(name="mock_check_login")
def fixture_mock_check_login(coresys: CoreSys):
    """Patch sys_auth.check_login."""
    with patch.object(coresys.auth, "check_login", new_callable=AsyncMock) as mock:
        yield mock


async def test_password_reset(
    api_client: TestClient,
    coresys: CoreSys,
    caplog: pytest.LogCaptureFixture,
    websession: MagicMock,
):
    """Test password reset api."""
    coresys.homeassistant.api.access_token = "abc123"
    # pylint: disable-next=protected-access
    coresys.homeassistant.api._access_token_expires = datetime.now(tz=UTC) + timedelta(
        days=1
    )

    websession.post = MagicMock(return_value=MockResponse(status=200))
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


@pytest.mark.parametrize("api_client", [TEST_ADDON_SLUG], indirect=True)
async def test_auth_json_success(
    api_client: TestClient, mock_check_login: AsyncMock, install_addon_ssh: Addon
):
    """Test successful JSON auth."""
    mock_check_login.return_value = True
    resp = await api_client.post("/auth", json={"username": "test", "password": "pass"})
    assert resp.status == 200


@pytest.mark.parametrize("api_client", [TEST_ADDON_SLUG], indirect=True)
async def test_auth_json_invalid_credentials(
    api_client: TestClient, mock_check_login: AsyncMock, install_addon_ssh: Addon
):
    """Test failed JSON auth due to invalid credentials."""
    mock_check_login.return_value = False
    resp = await api_client.post(
        "/auth", json={"username": "test", "password": "wrong"}
    )
    # Do we really want the API to return 400 here?
    assert resp.status == 400


@pytest.mark.parametrize("api_client", [TEST_ADDON_SLUG], indirect=True)
async def test_auth_json_empty_body(api_client: TestClient, install_addon_ssh: Addon):
    """Test JSON auth with empty body."""
    resp = await api_client.post(
        "/auth", data="", headers={"Content-Type": "application/json"}
    )
    assert resp.status == 400


@pytest.mark.parametrize("api_client", [TEST_ADDON_SLUG], indirect=True)
async def test_auth_json_invalid_json(api_client: TestClient, install_addon_ssh: Addon):
    """Test JSON auth with malformed JSON."""
    resp = await api_client.post(
        "/auth", data="{not json}", headers={"Content-Type": "application/json"}
    )
    assert resp.status == 400


@pytest.mark.parametrize("api_client", [TEST_ADDON_SLUG], indirect=True)
async def test_auth_urlencoded_success(
    api_client: TestClient, mock_check_login: AsyncMock, install_addon_ssh: Addon
):
    """Test successful URL-encoded auth."""
    mock_check_login.return_value = True
    resp = await api_client.post(
        "/auth",
        data="username=test&password=pass",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status == 200


@pytest.mark.parametrize("api_client", [TEST_ADDON_SLUG], indirect=True)
async def test_auth_urlencoded_failure(
    api_client: TestClient, mock_check_login: AsyncMock, install_addon_ssh: Addon
):
    """Test URL-encoded auth with invalid credentials."""
    mock_check_login.return_value = False
    resp = await api_client.post(
        "/auth",
        data="username=test&password=fail",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    # Do we really want the API to return 400 here?
    assert resp.status == 400


@pytest.mark.parametrize("api_client", [TEST_ADDON_SLUG], indirect=True)
async def test_auth_unsupported_content_type(
    api_client: TestClient, install_addon_ssh: Addon
):
    """Test auth with unsupported content type."""
    resp = await api_client.post(
        "/auth", data="something", headers={"Content-Type": "text/plain"}
    )
    # This probably should be 400 here for better consistency
    assert resp.status == 401


@pytest.mark.parametrize("api_client", [TEST_ADDON_SLUG], indirect=True)
async def test_auth_basic_auth(
    api_client: TestClient, mock_check_login: AsyncMock, install_addon_ssh: Addon
):
    """Test auth with BasicAuth header."""
    mock_check_login.return_value = True
    resp = await api_client.post(
        "/auth", headers={"Authorization": "Basic dGVzdDpwYXNz"}
    )
    assert resp.status == 200


@pytest.mark.parametrize("api_client", [TEST_ADDON_SLUG], indirect=True)
async def test_auth_basic_auth_failure(
    api_client: TestClient, mock_check_login: AsyncMock, install_addon_ssh: Addon
):
    """Test auth with BasicAuth header and failure."""
    mock_check_login.return_value = False
    resp = await api_client.post(
        "/auth", headers={"Authorization": "Basic dGVzdDpwYXNz"}
    )
    assert resp.status == 401


@pytest.mark.parametrize("api_client", ["local_example"], indirect=True)
async def test_auth_addon_no_auth_access(
    api_client: TestClient, install_addon_example: Addon
):
    """Test auth where add-on is not allowed to access auth API."""
    resp = await api_client.post("/auth", json={"username": "test", "password": "pass"})
    assert resp.status == 403


async def test_non_addon_token_no_auth_access(api_client: TestClient):
    """Test auth where add-on is not allowed to access auth API."""
    resp = await api_client.post("/auth", json={"username": "test", "password": "pass"})
    assert resp.status == 403
