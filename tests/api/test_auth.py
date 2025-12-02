"""Test auth API."""

from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from aiohttp.hdrs import WWW_AUTHENTICATE
from aiohttp.test_utils import TestClient
import pytest

from supervisor.addons.addon import Addon
from supervisor.coresys import CoreSys
from supervisor.exceptions import HomeAssistantAPIError, HomeAssistantWSError
from supervisor.homeassistant.api import HomeAssistantAPI

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


@pytest.mark.parametrize(
    ("post_mock", "expected_log"),
    [
        (
            MagicMock(return_value=MockResponse(status=400)),
            "The user 'john' is not registered",
        ),
        (
            MagicMock(side_effect=HomeAssistantAPIError("fail")),
            "Can't request password reset on Home Assistant: fail",
        ),
    ],
)
async def test_failed_password_reset(
    api_client: TestClient,
    coresys: CoreSys,
    caplog: pytest.LogCaptureFixture,
    websession: MagicMock,
    post_mock: MagicMock,
    expected_log: str,
):
    """Test failed password reset."""
    coresys.homeassistant.api.access_token = "abc123"
    # pylint: disable-next=protected-access
    coresys.homeassistant.api._access_token_expires = datetime.now(tz=UTC) + timedelta(
        days=1
    )

    websession.post = post_mock
    resp = await api_client.post(
        "/auth/reset", json={"username": "john", "password": "doe"}
    )
    assert resp.status == 400
    body = await resp.json()
    assert (
        body["message"]
        == "Unable to reset password for 'john'. Check supervisor logs for details (check with 'ha supervisor logs')"
    )
    assert body["error_key"] == "auth_password_reset_error"
    assert body["extra_fields"] == {
        "user": "john",
        "logs_command": "ha supervisor logs",
    }
    assert expected_log in caplog.text


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


@pytest.mark.parametrize(
    ("send_command_mock", "error_response", "expected_log"),
    [
        (
            AsyncMock(return_value=None),
            {
                "result": "error",
                "message": "Home Assistant returned invalid response of `None` instead of a list of users. Check Home Assistant logs for details (check with `ha core logs`)",
                "error_key": "auth_list_users_none_response_error",
                "extra_fields": {"none": "None", "logs_command": "ha core logs"},
            },
            "Home Assistant returned invalid response of `None` instead of a list of users. Check Home Assistant logs for details (check with `ha core logs`)",
        ),
        (
            AsyncMock(side_effect=HomeAssistantWSError("fail")),
            {
                "result": "error",
                "message": "Can't request listing users on Home Assistant. Check supervisor logs for details (check with 'ha supervisor logs')",
                "error_key": "auth_list_users_error",
                "extra_fields": {"logs_command": "ha supervisor logs"},
            },
            "Can't request listing users on Home Assistant: fail",
        ),
    ],
)
async def test_list_users_failure(
    api_client: TestClient,
    ha_ws_client: AsyncMock,
    caplog: pytest.LogCaptureFixture,
    send_command_mock: AsyncMock,
    error_response: dict[str, Any],
    expected_log: str,
):
    """Test failure listing users via API."""
    ha_ws_client.async_send_command = send_command_mock
    resp = await api_client.get("/auth/list")
    assert resp.status == 500
    result = await resp.json()
    assert result == error_response
    assert expected_log in caplog.text


@pytest.mark.parametrize(
    ("field", "api_client"),
    [("username", TEST_ADDON_SLUG), ("user", TEST_ADDON_SLUG)],
    indirect=["api_client"],
)
async def test_auth_json_success(
    api_client: TestClient,
    mock_check_login: AsyncMock,
    install_addon_ssh: Addon,
    field: str,
):
    """Test successful JSON auth."""
    mock_check_login.return_value = True
    resp = await api_client.post("/auth", json={field: "test", "password": "pass"})
    assert resp.status == 200


@pytest.mark.parametrize(
    ("user", "password", "api_client"),
    [
        (None, "password", TEST_ADDON_SLUG),
        ("user", None, TEST_ADDON_SLUG),
    ],
    indirect=["api_client"],
)
async def test_auth_json_failure_none(
    api_client: TestClient,
    mock_check_login: AsyncMock,
    install_addon_ssh: Addon,
    user: str | None,
    password: str | None,
):
    """Test failed JSON auth with none user or password."""
    mock_check_login.return_value = True
    resp = await api_client.post("/auth", json={"username": user, "password": password})
    assert resp.status == 401
    assert (
        resp.headers["WWW-Authenticate"]
        == 'Basic realm="Home Assistant Authentication"'
    )
    body = await resp.json()
    assert body["message"] == "Username and password must be strings"
    assert body["error_key"] == "auth_invalid_non_string_value_error"


@pytest.mark.parametrize("api_client", [TEST_ADDON_SLUG], indirect=True)
async def test_auth_json_invalid_credentials(
    api_client: TestClient, mock_check_login: AsyncMock, install_addon_ssh: Addon
):
    """Test failed JSON auth due to invalid credentials."""
    mock_check_login.return_value = False
    resp = await api_client.post(
        "/auth", json={"username": "test", "password": "wrong"}
    )
    assert WWW_AUTHENTICATE not in resp.headers
    assert resp.status == 401


@pytest.mark.parametrize("api_client", [TEST_ADDON_SLUG], indirect=True)
async def test_auth_json_empty_body(api_client: TestClient, install_addon_ssh: Addon):
    """Test JSON auth with empty body."""
    resp = await api_client.post(
        "/auth", data="", headers={"Content-Type": "application/json"}
    )
    assert resp.status == 401


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
    assert WWW_AUTHENTICATE not in resp.headers
    assert resp.status == 401


@pytest.mark.parametrize("api_client", [TEST_ADDON_SLUG], indirect=True)
async def test_auth_unsupported_content_type(
    api_client: TestClient, install_addon_ssh: Addon
):
    """Test auth with unsupported content type."""
    resp = await api_client.post(
        "/auth", data="something", headers={"Content-Type": "text/plain"}
    )
    assert "Basic realm" in resp.headers[WWW_AUTHENTICATE]
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


@pytest.mark.parametrize("api_client", [TEST_ADDON_SLUG], indirect=True)
@pytest.mark.usefixtures("install_addon_ssh")
async def test_auth_backend_login_failure(api_client: TestClient):
    """Test backend login failure on auth."""
    with (
        patch.object(HomeAssistantAPI, "check_api_state", return_value=True),
        patch.object(
            HomeAssistantAPI, "make_request", side_effect=HomeAssistantAPIError("fail")
        ),
    ):
        resp = await api_client.post(
            "/auth", json={"username": "test", "password": "pass"}
        )
    assert resp.status == 500
    body = await resp.json()
    assert (
        body["message"]
        == "Unable to validate authentication details with Home Assistant. Check supervisor logs for details (check with 'ha supervisor logs')"
    )
    assert body["error_key"] == "auth_home_assistant_api_validation_error"
    assert body["extra_fields"] == {"logs_command": "ha supervisor logs"}
