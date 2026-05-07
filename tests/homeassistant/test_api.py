"""Test Home Assistant API."""

from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

from awesomeversion import AwesomeVersion
import pytest

from supervisor.const import FeatureFlag
from supervisor.coresys import CoreSys
from supervisor.docker.const import ContainerState
from supervisor.docker.monitor import DockerContainerStateEvent
from supervisor.exceptions import HomeAssistantAPIError
from supervisor.homeassistant.api import APIState, HomeAssistantAPI
from supervisor.homeassistant.const import LANDINGPAGE

from tests.common import MockResponse

# --- get_config / get_core_state ---


async def test_get_config_success(coresys: CoreSys):
    """Test get_config returns valid config dictionary."""
    expected_config = {
        "latitude": 32.87336,
        "longitude": -117.22743,
        "elevation": 0,
        "unit_system": {
            "length": "km",
            "mass": "g",
            "temperature": "°C",
            "volume": "L",
        },
        "location_name": "Home",
        "time_zone": "America/Los_Angeles",
        "components": ["frontend", "config"],
        "version": "2025.8.0",
    }

    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value=expected_config)

    @asynccontextmanager
    async def mock_make_request(*_args, **_kwargs):
        yield mock_response

    with patch.object(
        type(coresys.homeassistant.api), "make_request", new=mock_make_request
    ):
        assert await coresys.homeassistant.api.get_config() == expected_config


@pytest.mark.parametrize(
    ("method", "bad_response", "match"),
    [
        ("get_config", None, "No config received"),
        ("get_config", ["not", "a", "dict"], "No config received"),
        ("get_core_state", None, "No state received"),
    ],
)
async def test_get_json_validation(
    coresys: CoreSys, method: str, bad_response, match: str
):
    """Test get_config/get_core_state raise on invalid responses."""
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value=bad_response)

    @asynccontextmanager
    async def mock_make_request(*_args, **_kwargs):
        yield mock_response

    with (
        patch.object(
            type(coresys.homeassistant.api), "make_request", new=mock_make_request
        ),
        pytest.raises(HomeAssistantAPIError, match=match),
    ):
        await getattr(coresys.homeassistant.api, method)()


async def test_get_config_api_error(coresys: CoreSys):
    """Test get_config propagates API errors."""
    mock_response = MagicMock(status=500)

    @asynccontextmanager
    async def mock_make_request(*_args, **_kwargs):
        yield mock_response

    with (
        patch.object(
            type(coresys.homeassistant.api), "make_request", new=mock_make_request
        ),
        pytest.raises(HomeAssistantAPIError, match="500"),
    ):
        await coresys.homeassistant.api.get_config()


# --- supports_unix_socket / use_unix_socket ---


@pytest.mark.parametrize(
    ("version", "flag_enabled", "expected"),
    [
        ("2026.4.0", True, True),
        ("2026.4.0", False, False),
        ("2026.5.1", True, True),
        ("2026.5.1", False, True),
        ("2026.6.0", False, True),
        ("2024.1.0", True, False),
        (LANDINGPAGE, True, False),
    ],
)
async def test_supports_unix_socket(
    coresys: CoreSys, version: str, flag_enabled: bool, expected: bool
):
    """Test supports_unix_socket based on Core version and feature flag."""
    coresys.homeassistant.version = AwesomeVersion(version)
    coresys.config.set_feature_flag(FeatureFlag.UNIX_SOCKET_CORE_API, flag_enabled)
    assert coresys.homeassistant.api.supports_unix_socket is expected


@pytest.mark.parametrize(
    ("version", "env", "expected"),
    [
        ("2024.1.0", [], False),
        ("2026.4.0", ["SUPERVISOR_CORE_API_SOCKET=/run/supervisor/core.sock"], True),
        ("2026.4.0", ["TZ=UTC", "SUPERVISOR_TOKEN=abc"], False),
    ],
)
async def test_use_unix_socket(
    coresys: CoreSys, version: str, env: list[str], expected: bool
):
    """Test use_unix_socket based on version and container env."""
    coresys.homeassistant.version = AwesomeVersion(version)
    coresys.config.set_feature_flag(FeatureFlag.UNIX_SOCKET_CORE_API, True)
    # pylint: disable-next=protected-access
    coresys.homeassistant.core.instance._meta = {"Config": {"Env": env}}
    assert coresys.homeassistant.api.use_unix_socket is expected


# --- api_url / ws_url ---


@pytest.mark.parametrize(
    ("use_unix", "expected_api_url", "expected_ws_url"),
    [
        (True, "http://localhost", "ws://localhost/api/websocket"),
        (False, "http://172.30.32.1:8123", "ws://172.30.32.1:8123/api/websocket"),
    ],
)
async def test_api_and_ws_urls(
    coresys: CoreSys, use_unix: bool, expected_api_url: str, expected_ws_url: str
):
    """Test api_url and ws_url for Unix socket and TCP transports."""
    with patch.object(type(coresys.homeassistant.api), "use_unix_socket", use_unix):
        assert coresys.homeassistant.api.api_url == expected_api_url
        assert coresys.homeassistant.api.ws_url == expected_ws_url


# --- connection lifecycle ---


@pytest.fixture
def real_get_api_state(coresys: CoreSys):
    """Restore real get_api_state (coresys fixture mocks it)."""
    api = coresys.homeassistant.api
    api.get_api_state = type(api).get_api_state.__get__(api)
    return api


async def test_connected_log_after_container_restart(
    coresys: CoreSys,
    real_get_api_state: HomeAssistantAPI,
    caplog: pytest.LogCaptureFixture,
):
    """Test 'Connected to Core' log reappears after container stop and reconnect."""
    api = coresys.homeassistant.api
    coresys.homeassistant.version = AwesomeVersion("2025.8.0")
    api.get_core_state = AsyncMock(
        return_value={"state": "RUNNING", "recorder_state": {}}
    )

    # First connection logs
    with patch.object(type(api), "use_unix_socket", False):
        await api.get_api_state()
    assert "Connected to Core via TCP" in caplog.text

    # Container stops
    caplog.clear()
    await api.container_state_changed(
        DockerContainerStateEvent(
            name="homeassistant",
            state=ContainerState.STOPPED,
            id="abc123",
            time=1234567890,
        )
    )

    # Reconnect logs again
    with patch.object(type(api), "use_unix_socket", False):
        await api.get_api_state()
    assert "Connected to Core via TCP" in caplog.text


async def test_container_state_changed_ignores_other_containers(
    coresys: CoreSys,
    real_get_api_state: HomeAssistantAPI,
    caplog: pytest.LogCaptureFixture,
):
    """Test container_state_changed ignores events from other containers."""
    api = coresys.homeassistant.api
    coresys.homeassistant.version = AwesomeVersion("2025.8.0")
    api.get_core_state = AsyncMock(
        return_value={"state": "RUNNING", "recorder_state": {}}
    )

    # First connection
    with patch.object(type(api), "use_unix_socket", False):
        await api.get_api_state()
    assert "Connected to Core via TCP" in caplog.text

    # Other container stops — should not reset
    caplog.clear()
    await api.container_state_changed(
        DockerContainerStateEvent(
            name="addon_local_ssh",
            state=ContainerState.STOPPED,
            id="abc123",
            time=1234567890,
        )
    )

    with patch.object(type(api), "use_unix_socket", False):
        await api.get_api_state()
    # Should NOT log again since connection state wasn't reset
    assert "Connected to Core" not in caplog.text


# --- get_api_state / check_api_state ---


@pytest.mark.parametrize(
    ("version", "core_state_response", "expected_state", "expected_check"),
    [
        (LANDINGPAGE, None, None, False),
        (None, None, None, False),
        (
            "2025.8.0",
            {"state": "RUNNING", "recorder_state": {}},
            APIState("RUNNING", False),
            True,
        ),
        (
            "2025.8.0",
            {"state": "NOT_RUNNING", "recorder_state": {}},
            APIState("NOT_RUNNING", False),
            False,
        ),
        (
            "2025.8.0",
            HomeAssistantAPIError("Connection failed"),
            None,
            False,
        ),
    ],
)
async def test_get_api_state(
    coresys: CoreSys,
    real_get_api_state: HomeAssistantAPI,
    version: str | None,
    core_state_response: dict | Exception | None,
    expected_state: APIState | None,
    expected_check: bool,
):
    """Test get_api_state and check_api_state for various scenarios."""
    coresys.homeassistant.version = (
        AwesomeVersion(version) if version and version != LANDINGPAGE else version
    )
    if isinstance(core_state_response, Exception):
        coresys.homeassistant.api.get_core_state = AsyncMock(
            side_effect=core_state_response
        )
    elif core_state_response is not None:
        coresys.homeassistant.api.get_core_state = AsyncMock(
            return_value=core_state_response
        )

    with patch.object(type(coresys.homeassistant.api), "use_unix_socket", False):
        assert await coresys.homeassistant.api.get_api_state() == expected_state
        assert await coresys.homeassistant.api.check_api_state() is expected_check


# --- make_request ---


async def test_make_request_not_running(coresys: CoreSys):
    """Test make_request raises when Core container is not running."""
    coresys.homeassistant.core.instance.is_running = AsyncMock(return_value=False)

    with pytest.raises(HomeAssistantAPIError, match="not running"):
        async with coresys.homeassistant.api.make_request("get", "api/test"):
            pass


@pytest.mark.usefixtures("websession")
async def test_make_request_tcp_with_token_fetch(coresys: CoreSys):
    """Test make_request fetches token via /auth/token and makes the request."""
    api = coresys.homeassistant.api

    # Mock /auth/token POST
    token_resp = MockResponse()
    token_resp.json = AsyncMock(
        return_value={"access_token": "test_token", "expires_in": 1800}
    )
    coresys.websession.post = MagicMock(return_value=token_resp)

    # Mock the actual API request
    api_resp = MagicMock(status=200)

    @asynccontextmanager
    async def mock_request(*_args, **_kwargs):
        yield api_resp

    coresys.websession.request = mock_request

    with patch.object(type(api), "use_unix_socket", False):
        async with api.make_request("get", "api/test") as resp:
            assert resp.status == 200

    # Verify token was fetched
    coresys.websession.post.assert_called_once()


@pytest.mark.usefixtures("websession")
async def test_make_request_tcp_timeout(coresys: CoreSys):
    """Test make_request wraps TimeoutError."""
    api = coresys.homeassistant.api
    coresys.websession.request = MagicMock(side_effect=TimeoutError("timed out"))

    with (
        patch.object(type(api), "use_unix_socket", False),
        patch.object(api, "_ensure_access_token", new_callable=AsyncMock),
        pytest.raises(HomeAssistantAPIError, match="timed out"),
    ):
        async with api.make_request("get", "api/test"):
            pass


# --- connect_websocket ---


async def test_connect_websocket_unix(coresys: CoreSys):
    """Test connect_websocket uses WSClient.connect for Unix socket."""
    coresys.homeassistant.core.instance.is_running = AsyncMock(return_value=True)
    mock_ws_client = MagicMock()
    with (
        patch.object(type(coresys.homeassistant.api), "use_unix_socket", True),
        patch(
            "supervisor.homeassistant.api.WSClient.connect",
            new_callable=AsyncMock,
            return_value=mock_ws_client,
        ) as mock_connect,
    ):
        result = await coresys.homeassistant.api.connect_websocket()

    assert result is mock_ws_client
    mock_connect.assert_called_once()


@pytest.mark.usefixtures("websession")
async def test_connect_websocket_tcp(coresys: CoreSys):
    """Test connect_websocket fetches token and connects with auth for TCP."""
    api = coresys.homeassistant.api
    mock_ws_client = MagicMock()

    # Mock the /auth/token endpoint to return a valid token
    token_resp = MockResponse()
    token_resp.json = AsyncMock(
        return_value={"access_token": "fresh_token", "expires_in": 1800}
    )
    coresys.websession.post = MagicMock(return_value=token_resp)

    with (
        patch.object(type(api), "use_unix_socket", False),
        patch(
            "supervisor.homeassistant.api.WSClient.connect_with_auth",
            new_callable=AsyncMock,
            return_value=mock_ws_client,
        ) as mock_connect,
    ):
        result = await api.connect_websocket()

    assert result is mock_ws_client
    # Verify token was fetched
    coresys.websession.post.assert_called_once()
    # Verify connect_with_auth was called with the fresh token
    mock_connect.assert_called_once()
    assert mock_connect.call_args.args[2] == "fresh_token"
