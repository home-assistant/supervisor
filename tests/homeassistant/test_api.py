"""Test Home Assistant API."""

import asyncio
from collections.abc import Generator
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

from awesomeversion import AwesomeVersion
import pytest

from supervisor.coresys import CoreSys
from supervisor.docker.const import ContainerState
from supervisor.docker.monitor import DockerContainerStateEvent
from supervisor.exceptions import (
    DockerError,
    HomeAssistantAPIError,
    HomeAssistantAuthError,
)
from supervisor.homeassistant.api import APIState, CoreHTTPConfig, HomeAssistantAPI
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
    ("version", "expected"),
    [
        ("2026.4.0", True),
        ("2026.5.1", True),
        ("2026.6.0", True),
        ("2024.1.0", False),
        (LANDINGPAGE, False),
    ],
)
async def test_supports_unix_socket(coresys: CoreSys, version: str, expected: bool):
    """Test supports_unix_socket based on Core version."""
    coresys.homeassistant.version = AwesomeVersion(version)
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
    # pylint: disable-next=protected-access
    coresys.homeassistant.core.instance._meta = {"Config": {"Env": env}}
    assert coresys.homeassistant.api.use_unix_socket is expected


# --- api_url / ws_url ---


@pytest.mark.parametrize(
    ("use_unix", "expected_api_url", "expected_ws_url"),
    [
        (True, "http://localhost", "ws://localhost/api/websocket"),
        (False, "http://172.30.32.1", "ws://172.30.32.1/api/websocket"),
    ],
)
async def test_api_and_ws_urls(
    coresys: CoreSys, use_unix: bool, expected_api_url: str, expected_ws_url: str
):
    """Test api_url and ws_url for Unix socket and TCP transports."""
    with patch.object(type(coresys.homeassistant.api), "use_unix_socket", use_unix):
        assert coresys.homeassistant.api.api_url == expected_api_url
        assert coresys.homeassistant.api.ws_url == expected_ws_url


@pytest.mark.parametrize(
    ("port", "ssl", "expected_api_url", "expected_ws_url"),
    [
        (80, False, "http://172.30.32.1", "ws://172.30.32.1/api/websocket"),
        (443, True, "https://172.30.32.1", "wss://172.30.32.1/api/websocket"),
        (
            8123,
            False,
            "http://172.30.32.1:8123",
            "ws://172.30.32.1:8123/api/websocket",
        ),
        (
            8123,
            True,
            "https://172.30.32.1:8123",
            "wss://172.30.32.1:8123/api/websocket",
        ),
        (80, True, "https://172.30.32.1:80", "wss://172.30.32.1:80/api/websocket"),
    ],
)
async def test_url_omits_default_scheme_port(
    coresys: CoreSys,
    port: int,
    ssl: bool,
    expected_api_url: str,
    expected_ws_url: str,
):
    """Test the port is only part of the url when the scheme doesn't imply it."""
    coresys.homeassistant.api_port = port
    coresys.homeassistant.api_ssl = ssl

    assert coresys.homeassistant.api_url == expected_api_url
    assert coresys.homeassistant.ws_url == expected_ws_url


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
            name="app_local_ssh",
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


# --- get_http_config ---

TEST_HTTP_CONFIG = {
    "port": 80,
    "ssl": False,
    "ssl_peer_certificate": False,
    "server_host": ["0.0.0.0", "::"],
}


async def test_get_http_config(coresys: CoreSys):
    """Test get_http_config parses the endpoint response."""
    coresys.homeassistant.version = AwesomeVersion("2026.8.0")
    api = coresys.homeassistant.api
    with (
        patch.object(type(api), "use_unix_socket", True),
        patch.object(api, "_get_json", return_value=TEST_HTTP_CONFIG),
    ):
        assert await api.get_http_config() == CoreHTTPConfig(
            port=80,
            ssl=False,
            ssl_peer_certificate=False,
            server_host=["0.0.0.0", "::"],
        )


@pytest.mark.parametrize(
    ("use_unix_socket", "version", "response"),
    [
        # TCP fallback: the endpoint is socket-only.
        (False, "2026.8.0", TEST_HTTP_CONFIG),
        # Core version without the endpoint.
        (True, "2026.7.0", TEST_HTTP_CONFIG),
        # Endpoint request fails.
        (True, "2026.8.0", HomeAssistantAPIError("Core API return 404")),
        # Malformed responses.
        (True, "2026.8.0", {"port": 80}),
        (True, "2026.8.0", {**TEST_HTTP_CONFIG, "port": "no-number"}),
        (True, "2026.8.0", {**TEST_HTTP_CONFIG, "server_host": 42}),
    ],
)
async def test_get_http_config_unavailable(
    coresys: CoreSys,
    use_unix_socket: bool,
    version: str,
    response: dict | Exception,
):
    """Test get_http_config returns None when the config cannot be fetched."""
    coresys.homeassistant.version = AwesomeVersion(version)
    api = coresys.homeassistant.api
    get_json = (
        AsyncMock(side_effect=response)
        if isinstance(response, Exception)
        else AsyncMock(return_value=response)
    )
    with (
        patch.object(type(api), "use_unix_socket", use_unix_socket),
        patch.object(api, "_get_json", get_json),
    ):
        assert await api.get_http_config() is None


async def test_http_config_pulled_on_connect(
    coresys: CoreSys, real_get_api_state: HomeAssistantAPI
):
    """Test connection parameters refresh from Core's HTTP config on connect."""
    api = coresys.homeassistant.api
    coresys.homeassistant.version = AwesomeVersion("2026.8.0")
    api.get_core_state = AsyncMock(
        return_value={"state": "RUNNING", "recorder_state": {}}
    )
    coresys.homeassistant.save_data = AsyncMock()
    coresys.homeassistant.api_port = 8123

    assert coresys.homeassistant.http_server_host is None

    with (
        patch.object(type(api), "use_unix_socket", True),
        patch.object(api, "_get_json", return_value=TEST_HTTP_CONFIG) as get_json,
    ):
        await api.get_api_state()
        assert coresys.homeassistant.api_port == 80
        assert coresys.homeassistant.api_ssl is False
        assert coresys.homeassistant.http_server_host == ["0.0.0.0", "::"]
        coresys.homeassistant.save_data.assert_awaited_once()

        # Already connected: no pull on subsequent checks.
        get_json.reset_mock()
        await api.get_api_state()
        get_json.assert_not_awaited()

    # Container restart resets the connection; the config is pulled again.
    await api.container_state_changed(
        DockerContainerStateEvent(
            name="homeassistant",
            state=ContainerState.STOPPED,
            id="abc123",
            time=1234567890,
        )
    )
    with (
        patch.object(type(api), "use_unix_socket", True),
        patch.object(api, "_get_json", return_value=TEST_HTTP_CONFIG) as get_json,
    ):
        await api.get_api_state()
        get_json.assert_awaited_once_with("api/core/http_config")


async def test_http_config_unchanged_not_saved(
    coresys: CoreSys, real_get_api_state: HomeAssistantAPI
):
    """Test unchanged connection parameters are not saved to disk."""
    api = coresys.homeassistant.api
    coresys.homeassistant.version = AwesomeVersion("2026.8.0")
    api.get_core_state = AsyncMock(
        return_value={"state": "RUNNING", "recorder_state": {}}
    )
    coresys.homeassistant.save_data = AsyncMock()

    config = {**TEST_HTTP_CONFIG, "server_host": ["172.30.32.1"]}
    with (
        patch.object(type(api), "use_unix_socket", True),
        patch.object(api, "_get_json", return_value=config),
    ):
        await api.get_api_state()

    coresys.homeassistant.save_data.assert_not_awaited()
    # The bind hosts are still updated for the frontend reachability check.
    assert coresys.homeassistant.http_server_host == ["172.30.32.1"]


async def test_http_config_reset_when_unavailable(
    coresys: CoreSys, real_get_api_state: HomeAssistantAPI
):
    """Test bind hosts reset when the HTTP config cannot be fetched.

    After a downgrade to a Core without the endpoint, reachability decisions
    must not use the previous Core's binds.
    """
    api = coresys.homeassistant.api
    coresys.homeassistant.version = AwesomeVersion("2026.8.0")
    api.get_core_state = AsyncMock(
        return_value={"state": "RUNNING", "recorder_state": {}}
    )
    coresys.homeassistant.http_server_host = ["172.30.32.1"]

    with patch.object(type(api), "use_unix_socket", False):
        await api.get_api_state()

    assert coresys.homeassistant.http_server_host is None


@pytest.mark.parametrize(
    "slow_request",
    [
        pytest.param("get_core_state", id="core_state"),
        pytest.param("_get_json", id="http_config"),
    ],
)
async def test_connect_discarded_on_container_stop_in_flight(
    coresys: CoreSys,
    real_get_api_state: HomeAssistantAPI,
    caplog: pytest.LogCaptureFixture,
    slow_request: str,
):
    """Test a Core stop during the connect requests does not mark Core connected."""
    api = coresys.homeassistant.api
    coresys.homeassistant.version = AwesomeVersion("2026.8.0")
    coresys.homeassistant.save_data = AsyncMock()
    coresys.homeassistant.api_port = 8123
    mocks = {
        "get_core_state": AsyncMock(
            return_value={"state": "RUNNING", "recorder_state": {}}
        ),
        "_get_json": AsyncMock(return_value=TEST_HTTP_CONFIG),
    }
    started = asyncio.Event()
    release = asyncio.Event()
    response = mocks[slow_request].return_value

    async def slow(*_: str) -> dict:
        started.set()
        await release.wait()
        return response

    mocks[slow_request].side_effect = slow

    with (
        patch.object(type(api), "use_unix_socket", True),
        patch.multiple(api, **mocks),
    ):
        state = asyncio.create_task(api.get_api_state())
        await started.wait()
        await api.container_state_changed(core_state_event(ContainerState.STOPPED))
        release.set()

        assert await state == APIState("RUNNING", False)
        assert "Connected to Core" not in caplog.text
        assert coresys.homeassistant.api_port == 8123
        assert coresys.homeassistant.http_server_host is None
        coresys.homeassistant.save_data.assert_not_awaited()

        # The next check connects and refreshes the HTTP config.
        assert await api.get_api_state() == APIState("RUNNING", False)
        assert "Connected to Core via Unix socket" in caplog.text
        assert coresys.homeassistant.api_port == 80
        assert coresys.homeassistant.http_server_host == ["0.0.0.0", "::"]
        coresys.homeassistant.save_data.assert_awaited_once()


# --- make_request ---


async def test_make_request_not_running(coresys: CoreSys):
    """Test make_request raises when Core container is not running."""
    coresys.homeassistant.core.instance.is_running = AsyncMock(return_value=False)

    with pytest.raises(HomeAssistantAPIError, match="not running"):
        async with coresys.homeassistant.api.make_request("get", "api/test"):
            pass


async def test_make_request_running_check_docker_error(coresys: CoreSys):
    """Test make_request wraps Docker errors from running check."""
    coresys.homeassistant.core.instance.is_running = AsyncMock(
        side_effect=DockerError("docker failure")
    )

    with pytest.raises(
        HomeAssistantAPIError, match="Unable to determine if Core container is running"
    ):
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
async def test_make_request_sends_path_pre_encoded(coresys: CoreSys):
    """Test make_request sends the path byte-for-byte, without re-decoding.

    yarl normalizes percent-encoded unreserved characters (%5F -> _) unless the
    URL is marked as already encoded. The proxy relies on the bytes it checked
    being the bytes that reach Core.
    """
    api = coresys.homeassistant.api
    api_resp = MagicMock(status=200)

    @asynccontextmanager
    async def mock_request(*_args, **_kwargs):
        yield api_resp

    request_mock = MagicMock(side_effect=mock_request)
    coresys.websession.request = request_mock

    with (
        patch.object(type(api), "use_unix_socket", False),
        patch.object(api, "_ensure_access_token", new_callable=AsyncMock),
    ):
        async with api.make_request("get", "api/hassio%5Fauth/a%2Fb") as resp:
            assert resp.status == 200

    url = request_mock.call_args.args[1]
    assert url.raw_path == "/api/hassio%5Fauth/a%2Fb"
    assert str(url) == "http://172.30.32.1/api/hassio%5Fauth/a%2Fb"


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


@pytest.mark.usefixtures("websession")
async def test_make_request_tcp_401_refreshes_token_once(coresys: CoreSys):
    """Test a 401 over TCP drops the token and retries once."""
    api = coresys.homeassistant.api
    api._access_token = "stale"  # pylint: disable=protected-access
    coresys.websession.request = MagicMock(
        side_effect=[MockResponse(status=401), MockResponse(status=200)]
    )

    with (
        patch.object(type(api), "use_unix_socket", False),
        patch.object(api, "_ensure_access_token", new_callable=AsyncMock) as ensure,
    ):
        async with api.make_request("get", "api/test") as resp:
            assert resp.status == 200

    assert coresys.websession.request.call_count == 2
    assert ensure.await_count == 2


@pytest.mark.usefixtures("websession")
async def test_make_request_tcp_401_after_refresh_raises(
    coresys: CoreSys, caplog: pytest.LogCaptureFixture
):
    """Test a 401 with a freshly refreshed token raises HomeAssistantAuthError."""
    api = coresys.homeassistant.api
    coresys.websession.request = MagicMock(
        side_effect=[MockResponse(status=401), MockResponse(status=401)]
    )

    with (
        patch.object(type(api), "use_unix_socket", False),
        patch.object(api, "_ensure_access_token", new_callable=AsyncMock),
        pytest.raises(HomeAssistantAuthError),
    ):
        async with api.make_request("get", "api/test"):
            pass

    assert coresys.websession.request.call_count == 2
    assert (
        "Home Assistant rejected Supervisor credentials on api/test "
        "after token refresh" in caplog.text
    )


@pytest.mark.usefixtures("websession")
async def test_make_request_unix_socket_401_raises(
    coresys: CoreSys, caplog: pytest.LogCaptureFixture
):
    """Test a 401 over the Unix socket raises HomeAssistantAuthError right away."""
    api = coresys.homeassistant.api
    session = MagicMock()
    session.request = MagicMock(return_value=MockResponse(status=401))

    with (
        patch.object(type(api), "use_unix_socket", True),
        patch.object(
            type(api), "session", new_callable=PropertyMock, return_value=session
        ),
        pytest.raises(HomeAssistantAuthError),
    ):
        async with api.make_request("get", "api/test"):
            pass

    session.request.assert_called_once()
    assert "Home Assistant rejected Supervisor credentials on api/test" in caplog.text


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


async def test_connect_websocket_running_check_docker_error(coresys: CoreSys):
    """Test connect_websocket wraps Docker errors from running check."""
    coresys.homeassistant.core.instance.is_running = AsyncMock(
        side_effect=DockerError("docker failure")
    )

    with pytest.raises(
        HomeAssistantAPIError, match="Unable to determine if Core container is running"
    ):
        await coresys.homeassistant.api.connect_websocket()


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


# --- Core container running state ---


def core_state_event(state: ContainerState) -> DockerContainerStateEvent:
    """Return a container state event for the Core container."""
    return DockerContainerStateEvent(
        name="homeassistant", state=state, id="abc123", time=1234567890
    )


@pytest.mark.parametrize(
    "state",
    [
        pytest.param(ContainerState.RUNNING, id="running"),
        pytest.param(ContainerState.HEALTHY, id="healthy"),
        pytest.param(ContainerState.UNHEALTHY, id="unhealthy"),
    ],
)
@pytest.mark.usefixtures("websession")
async def test_make_request_skips_inspect_when_core_running(
    coresys: CoreSys, state: ContainerState
):
    """Test make_request trusts container state events instead of inspecting."""
    api = coresys.homeassistant.api
    coresys.websession.request = MagicMock(
        side_effect=lambda *_args, **_kwargs: MockResponse(status=200)
    )
    await api.container_state_changed(core_state_event(state))

    with (
        patch.object(type(api), "use_unix_socket", False),
        patch.object(api, "_ensure_access_token", new_callable=AsyncMock),
    ):
        for _ in range(5):
            async with api.make_request("get", "api/test") as resp:
                assert resp.status == 200

    coresys.homeassistant.core.instance.is_running.assert_not_awaited()
    assert coresys.websession.request.call_count == 5


@pytest.mark.parametrize(
    "stopped_state",
    [
        pytest.param(ContainerState.STOPPED, id="stopped"),
        pytest.param(ContainerState.FAILED, id="failed"),
    ],
)
@pytest.mark.usefixtures("websession")
async def test_make_request_after_core_stopped_and_started(
    coresys: CoreSys, stopped_state: ContainerState
):
    """Test make_request fails fast once Core stopped and recovers on start."""
    api = coresys.homeassistant.api
    is_running = coresys.homeassistant.core.instance.is_running
    is_running.return_value = False
    coresys.websession.request = MagicMock(
        side_effect=lambda *_args, **_kwargs: MockResponse(status=200)
    )
    await api.container_state_changed(core_state_event(ContainerState.RUNNING))
    await api.container_state_changed(core_state_event(stopped_state))

    with (
        patch.object(type(api), "use_unix_socket", False),
        patch.object(api, "_ensure_access_token", new_callable=AsyncMock),
    ):
        with pytest.raises(HomeAssistantAPIError, match="not running"):
            async with api.make_request("get", "api/test"):
                pass
        is_running.assert_awaited_once()
        coresys.websession.request.assert_not_called()

        await api.container_state_changed(core_state_event(ContainerState.RUNNING))
        async with api.make_request("get", "api/test") as resp:
            assert resp.status == 200

    is_running.assert_awaited_once()
    coresys.websession.request.assert_called_once()


async def test_make_request_ignores_other_container_running(coresys: CoreSys):
    """Test a running event of another container does not skip the inspect."""
    api = coresys.homeassistant.api
    coresys.homeassistant.core.instance.is_running = AsyncMock(return_value=False)
    await api.container_state_changed(
        DockerContainerStateEvent(
            name="app_local_ssh",
            state=ContainerState.RUNNING,
            id="abc123",
            time=1234567890,
        )
    )

    with pytest.raises(HomeAssistantAPIError, match="not running"):
        async with api.make_request("get", "api/test"):
            pass


# --- check_api_state caching ---


@pytest.fixture(name="core_state")
def fixture_core_state(
    coresys: CoreSys, real_get_api_state: HomeAssistantAPI
) -> Generator[AsyncMock]:
    """Mock the Core state request of a Core supporting it."""
    coresys.homeassistant.version = AwesomeVersion("2025.8.0")
    real_get_api_state.get_core_state = AsyncMock(
        return_value={"state": "RUNNING", "recorder_state": {}}
    )
    with patch.object(type(real_get_api_state), "use_unix_socket", False):
        yield real_get_api_state.get_core_state


async def test_check_api_state_cached(coresys: CoreSys, core_state: AsyncMock):
    """Test repeated check_api_state calls share one Core state request."""
    for _ in range(10):
        assert await coresys.homeassistant.api.check_api_state() is True

    core_state.assert_awaited_once()


async def test_check_api_state_concurrent_calls_share_request(
    coresys: CoreSys, core_state: AsyncMock
):
    """Test concurrent check_api_state calls wait on the same Core state request."""
    release = asyncio.Event()

    async def slow_core_state() -> dict[str, str]:
        await release.wait()
        return {"state": "RUNNING"}

    core_state.side_effect = slow_core_state
    checks = asyncio.gather(
        *(coresys.homeassistant.api.check_api_state() for _ in range(10))
    )
    await asyncio.sleep(0)
    release.set()

    assert await checks == [True] * 10
    core_state.assert_awaited_once()


@pytest.mark.parametrize(
    ("response", "expected_check", "expected_requests"),
    [
        pytest.param(
            {"state": "NOT_RUNNING", "recorder_state": {}}, False, 3, id="not_running"
        ),
        pytest.param(
            HomeAssistantAPIError("Connection failed"), False, 3, id="api_error"
        ),
        pytest.param(
            {
                "state": "NOT_RUNNING",
                "recorder_state": {
                    "migration_in_progress": True,
                    "migration_is_live": False,
                },
            },
            True,
            1,
            id="offline_db_migration",
        ),
    ],
)
async def test_check_api_state_caches_only_up(
    coresys: CoreSys,
    core_state: AsyncMock,
    response: dict | Exception,
    expected_check: bool,
    expected_requests: int,
):
    """Test only a Core state that allows API use is cached."""
    core_state.side_effect = [response] * 3

    for _ in range(3):
        assert await coresys.homeassistant.api.check_api_state() is expected_check

    assert core_state.await_count == expected_requests


async def test_check_api_state_cache_expires(coresys: CoreSys, core_state: AsyncMock):
    """Test the cached API state expires after a few seconds."""
    with patch("supervisor.homeassistant.api.monotonic") as monotonic:
        monotonic.return_value = 100.0
        assert await coresys.homeassistant.api.check_api_state() is True
        monotonic.return_value = 104.9
        assert await coresys.homeassistant.api.check_api_state() is True
        core_state.assert_awaited_once()

        monotonic.return_value = 105.0
        assert await coresys.homeassistant.api.check_api_state() is True

    assert core_state.await_count == 2


@pytest.mark.parametrize(
    "state",
    [pytest.param(state, id=str(state)) for state in ContainerState],
)
async def test_check_api_state_cache_invalidated_on_container_state(
    coresys: CoreSys, core_state: AsyncMock, state: ContainerState
):
    """Test any Core container state change drops the cached API state."""
    api = coresys.homeassistant.api
    assert await api.check_api_state() is True

    await api.container_state_changed(core_state_event(state))
    assert await api.check_api_state() is True

    assert core_state.await_count == 2


async def test_check_api_state_cache_kept_on_other_container_state(
    coresys: CoreSys, core_state: AsyncMock
):
    """Test state changes of other containers keep the cached API state."""
    api = coresys.homeassistant.api
    assert await api.check_api_state() is True

    await api.container_state_changed(
        DockerContainerStateEvent(
            name="app_local_ssh",
            state=ContainerState.STOPPED,
            id="abc123",
            time=1234567890,
        )
    )
    assert await api.check_api_state() is True

    core_state.assert_awaited_once()


async def test_check_api_state_in_flight_result_not_cached_after_state_change(
    coresys: CoreSys, core_state: AsyncMock
):
    """Test a Core state request racing a container state change is not cached."""
    api = coresys.homeassistant.api
    release = asyncio.Event()

    async def slow_core_state() -> dict[str, str]:
        await release.wait()
        return {"state": "RUNNING"}

    core_state.side_effect = slow_core_state
    check = asyncio.create_task(api.check_api_state())
    await asyncio.sleep(0)
    await api.container_state_changed(core_state_event(ContainerState.STOPPED))
    release.set()

    assert await check is True
    assert await api.check_api_state() is True
    assert core_state.await_count == 2
