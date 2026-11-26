"""Home Assistant control object."""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import logging
from pathlib import Path, PurePath
from typing import TYPE_CHECKING, Any

import aiohttp
from aiohttp import hdrs
from awesomeversion import AwesomeVersion
from multidict import MultiMapping
from yarl import URL

from ..const import SERVER_SOFTWARE, SOCKET_NAME_CORE
from ..coresys import CoreSys, CoreSysAttributes
from ..docker.const import ENV_CORE_API_SOCKET, ContainerState
from ..docker.monitor import DockerContainerStateEvent
from ..exceptions import (
    HomeAssistantAPIError,
    HomeAssistantAuthError,
    HomeAssistantWSConnectionError,
)
from ..utils import version_is_new_enough
from .const import LANDINGPAGE
from .validate import core_binds_app_sockets
from .websocket import WSClient

if TYPE_CHECKING:
    from ..apps.app import App

_LOGGER: logging.Logger = logging.getLogger(__name__)

# Core identifies an app by its socket, the host part is never resolved
APP_API_URL = "http://localhost"
APP_WS_URL = "ws://localhost/api/websocket"

CORE_UNIX_SOCKET_MIN_VERSION: AwesomeVersion = AwesomeVersion(
    "2026.4.0.dev202603250907"
)
GET_CORE_STATE_MIN_VERSION: AwesomeVersion = AwesomeVersion("2023.8.0.dev20230720")
# First nightly after https://github.com/home-assistant/core/pull/176976
# added the endpoint. Requesting it from a dev build without the endpoint
# fails gracefully (404 -> None).
HTTP_CONFIG_MIN_VERSION: AwesomeVersion = AwesomeVersion("2026.8.0.dev202607280000")


@dataclass(frozen=True)
class APIState:
    """Container for API state response."""

    core_state: str
    offline_db_migration: bool


@dataclass(frozen=True)
class CoreHTTPConfig:
    """Live HTTP server configuration reported by Core."""

    port: int
    ssl: bool
    ssl_peer_certificate: bool
    server_host: list[str]


class HomeAssistantAPI(CoreSysAttributes):
    """Home Assistant core object for handle it."""

    def __init__(self, coresys: CoreSys):
        """Initialize Home Assistant object."""
        self.coresys: CoreSys = coresys

        # We don't persist access tokens. Instead we fetch new ones when needed
        self._access_token: str | None = None
        self._access_token_expires: datetime | None = None
        self._token_lock: asyncio.Lock = asyncio.Lock()
        self._unix_session: aiohttp.ClientSession | None = None
        self._app_sessions: dict[str, aiohttp.ClientSession] = {}
        self._core_connected: bool = False
        self._core_used_supervisor_socket: bool = False
        self._core_container_running: bool | None = None

    @property
    def supports_unix_socket(self) -> bool:
        """Return True if the installed Core version supports Unix socket communication.

        Enabled by default for Core >= CORE_UNIX_SOCKET_MIN_VERSION.

        Used to decide whether to configure the env var when starting Core.
        """
        return (
            self.sys_homeassistant.version is not None
            and self.sys_homeassistant.version != LANDINGPAGE
            and version_is_new_enough(
                self.sys_homeassistant.version, CORE_UNIX_SOCKET_MIN_VERSION
            )
        )

    def _supervisor_view_of_core_socket(self, core_path: str) -> Path:
        """Map Core's view of its socket path to Supervisor's view of the same file."""
        # Core mounts the run folder at the same path as on the host
        try:
            relative = PurePath(core_path).relative_to(self.sys_config.path_extern_run)
        except ValueError:
            return self.sys_config.path_run / SOCKET_NAME_CORE
        return self.sys_config.path_run / relative

    @property
    def core_socket_path(self) -> Path | None:
        """Return the running Core container's Unix socket path, None for TCP.

        Checks both version support and that the container was actually started
        with the SUPERVISOR_CORE_API_SOCKET env var. The path is read from that
        env var, so it always matches how the running container was started,
        even when Core is still running with a container started by an older
        Supervisor.

        Raises HomeAssistantAPIError without container metadata, i.e. when no
        Core container exists to connect to.
        """
        if not self.supports_unix_socket:
            return None
        instance = self.sys_homeassistant.core.instance
        if not instance.attached:
            raise HomeAssistantAPIError(
                "Cannot determine Core connection mode: container metadata not available"
            )
        for env in instance.meta_config.get("Env", []):
            name, _, value = env.partition("=")
            if name == ENV_CORE_API_SOCKET:
                return self._supervisor_view_of_core_socket(value)
        return None

    @property
    def core_used_supervisor_socket(self) -> bool:
        """Return True if the running Core container has called Supervisor's socket.

        Such a Core makes all of its own Supervisor requests over the socket.
        """
        return self._core_used_supervisor_socket

    @core_used_supervisor_socket.setter
    def core_used_supervisor_socket(self, value: bool) -> None:
        """Set if the running Core container has called Supervisor's socket."""
        self._core_used_supervisor_socket = value

    @property
    def use_unix_socket(self) -> bool:
        """Return True if the running Core container is configured for Unix socket.

        Raises HomeAssistantAPIError without container metadata, i.e. when no
        Core container exists to connect to.
        """
        return self.core_socket_path is not None

    @property
    def session(self) -> aiohttp.ClientSession:
        """Return session for Core communication.

        Uses a Unix socket session when the installed Core version supports it,
        otherwise falls back to the default TCP websession. If the socket does
        not exist yet (e.g. during Core startup), requests will fail with a
        connection error handled by the caller.
        """
        if not self.use_unix_socket:
            return self.sys_websession

        if self._unix_session is None or self._unix_session.closed:
            # Unlike Core's IP over TCP, "localhost" lets a real jar store cookies
            # from any Core view and replay them on every later request
            self._unix_session = aiohttp.ClientSession(
                connector=aiohttp.UnixConnector(path=str(self.core_socket_path)),
                cookie_jar=aiohttp.DummyCookieJar(),
                headers={hdrs.USER_AGENT: SERVER_SOFTWARE},
            )
        return self._unix_session

    def session_for_app(self, app: App) -> aiohttp.ClientSession | None:
        """Return the session forwarding an app's requests to Core as the app.

        None while Core does not bind a socket for each app, Supervisor's own
        session applies then. Never falls back to it once Core does, a missing
        socket fails the request instead.
        """
        if not app.with_core_socket or not core_binds_app_sockets(
            self.sys_homeassistant.version
        ):
            return None

        session = self._app_sessions.get(app.slug)
        if session is None or session.closed:
            session = self._app_sessions[app.slug] = aiohttp.ClientSession(
                connector=aiohttp.UnixConnector(
                    path=str(app.path_run_core / SOCKET_NAME_CORE)
                ),
                cookie_jar=aiohttp.DummyCookieJar(),
                headers={hdrs.USER_AGENT: SERVER_SOFTWARE},
            )
        return session

    async def close_app_session(self, slug: str) -> None:
        """Close the session forwarding an app's requests to Core."""
        if (session := self._app_sessions.pop(slug, None)) and not session.closed:
            await session.close()

    async def _close_app_sessions(self) -> None:
        """Close the sessions forwarding apps' requests to Core."""
        for slug in list(self._app_sessions):
            await self.close_app_session(slug)

    @property
    def api_url(self) -> str:
        """Return API base url for internal Supervisor to Core communication."""
        if self.use_unix_socket:
            return "http://localhost"
        return self.sys_homeassistant.api_url

    @property
    def ws_url(self) -> str:
        """Return WebSocket url for internal Supervisor to Core communication."""
        if self.use_unix_socket:
            return "ws://localhost/api/websocket"
        return self.sys_homeassistant.ws_url

    async def container_state_changed(self, event: DockerContainerStateEvent) -> None:
        """Process Core container state changes."""
        if event.name != self.sys_homeassistant.core.instance.name:
            return

        # A pending or failed healthcheck still means the process is up
        self._core_container_running = event.state in (
            ContainerState.RUNNING,
            ContainerState.STARTING,
            ContainerState.HEALTHY,
            ContainerState.UNHEALTHY,
        )
        if event.state not in (ContainerState.STOPPED, ContainerState.FAILED):
            return

        self._core_connected = False
        self._core_used_supervisor_socket = False
        if self._unix_session and not self._unix_session.closed:
            await self._unix_session.close()
            self._unix_session = None
        await self._close_app_sessions()

    async def close(self) -> None:
        """Close the Unix socket sessions."""
        if self._unix_session and not self._unix_session.closed:
            await self._unix_session.close()
            self._unix_session = None
        await self._close_app_sessions()

    async def _ensure_access_token(self) -> None:
        """Ensure there is a valid access token.

        Raises:
            HomeAssistantAuthError: When we cannot get a valid token
            aiohttp.ClientError: On network or connection errors
            TimeoutError: On request timeouts

        """
        # Fast path check without lock (avoid unnecessary locking
        # for the majority of calls).
        if (
            self._access_token
            and self._access_token_expires
            and self._access_token_expires > datetime.now(tz=UTC)
        ):
            return

        async with self._token_lock:
            # Double-check after acquiring lock (avoid race condition)
            if (
                self._access_token
                and self._access_token_expires
                and self._access_token_expires > datetime.now(tz=UTC)
            ):
                return

            async with self.sys_websession.post(
                f"{self.sys_homeassistant.api_url}/auth/token",
                timeout=aiohttp.ClientTimeout(total=30),
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": self.sys_homeassistant.refresh_token,
                },
                ssl=False,
            ) as resp:
                if resp.status != 200:
                    raise HomeAssistantAuthError(
                        "Can't update Home Assistant access token!", _LOGGER.error
                    )

                _LOGGER.info("Updated Home Assistant API token")
                tokens = await resp.json()
                self._access_token = tokens["access_token"]
                self._access_token_expires = datetime.now(tz=UTC) + timedelta(
                    seconds=tokens["expires_in"]
                )

    def _request_error[ErrorT: HomeAssistantAPIError](
        self, url: URL | str, err: Exception, error_type: type[ErrorT]
    ) -> ErrorT:
        """Describe a failed request, naming a stopped Core container as the cause."""
        # Container state comes from Docker events, None until the first one
        if self._core_container_running is False:
            _LOGGER.debug("Error on call %s: Core container is not running", url)
            return error_type("Core container is not running")
        message = str(err) or type(err).__name__
        _LOGGER.debug("Error on call %s: %s", url, message)
        return error_type(message)

    async def connect_websocket(self, app: App | None = None) -> WSClient:
        """Connect a WebSocket to Core, handling auth as appropriate.

        For Unix socket connections, no authentication is needed.
        For TCP connections, handles token management with one retry
        on auth failure. With an app, connects as that app (see session_for_app).

        Raises:
            HomeAssistantAPIError: On connection or auth failure.

        """
        unix_session: aiohttp.ClientSession | None
        if app and (app_session := self.session_for_app(app)):
            unix_session, url = app_session, APP_WS_URL
        elif self.use_unix_socket:
            unix_session, url = self.session, self.ws_url
        else:
            unix_session, url = None, self.ws_url

        try:
            if unix_session:
                return await WSClient.connect(unix_session, url)

            for attempt in (1, 2):
                try:
                    await self._ensure_access_token()
                    assert self._access_token
                    return await WSClient.connect_with_auth(
                        self.session, url, self._access_token
                    )
                except HomeAssistantAuthError:
                    self._access_token = None
                    if attempt == 2:
                        raise
        except (
            HomeAssistantWSConnectionError,
            TimeoutError,
            aiohttp.ClientError,
        ) as err:
            raise self._request_error(url, err, HomeAssistantWSConnectionError) from err

        # Unreachable, but satisfies type checker
        raise RuntimeError("Unreachable")

    @asynccontextmanager
    async def make_request(
        self,
        method: str,
        path: str,
        json: dict[str, Any] | None = None,
        content_type: str | None = None,
        data: Any = None,
        timeout: int | None = 30,
        params: MultiMapping[str] | None = None,
        headers: dict[str, str] | None = None,
        app: App | None = None,
    ) -> AsyncIterator[aiohttp.ClientResponse]:
        """Async context manager to make requests to Home Assistant Core API.

        This context manager handles transport and authentication automatically.
        For Unix socket connections, requests are made directly without auth.
        For TCP connections, it manages access tokens and retries once on 401.
        It yields the HTTP response for the caller to handle.

        Error Handling:
        - HTTP error status codes (4xx, 5xx) are preserved in the response
        - Authentication is handled transparently (TCP only)
        - Network/connection failures raise HomeAssistantAPIError
        - No logging is performed - callers should handle logging as needed

        Args:
            method: HTTP method (get, post, etc.)
            path: API path relative to Home Assistant base URL. Sent as-is:
                it must already be percent-encoded where needed and is not
                decoded or normalized again.
            json: JSON data to send in request body
            content_type: Override content-type header
            data: Raw data to send in request body
            timeout: Request timeout in seconds
            params: URL query parameters
            headers: Additional HTTP headers
            app: Make the request as this app (see session_for_app). Core's
                answer then goes to the app, a 401 included

        Yields:
            aiohttp.ClientResponse: The HTTP response object

        Raises:
            HomeAssistantAPIError: When request cannot be completed due to
                network errors, timeouts, or connection failures
            HomeAssistantAuthError: When Core rejects Supervisor's own
                credentials (HTTP 401), after one token refresh over TCP

        """
        # As an app, a 401 is Core's answer for the app, not about Supervisor's
        # credentials
        if app and (app_session := self.session_for_app(app)):
            session, base_url, use_token, as_app = app_session, APP_API_URL, False, True
        else:
            session, base_url, as_app = self.session, self.api_url, False
            use_token = not self.use_unix_socket

        # encoded=True makes yarl send the path byte-for-byte. Without it, yarl
        # would normalize percent-encoded unreserved characters (e.g. %5F -> _),
        # which lets a path that passed a deny check upstream turn into a
        # different one on the wire.
        url = URL(f"{base_url}/{path}", encoded=True)
        headers = headers or {}
        client_timeout = aiohttp.ClientTimeout(total=timeout)

        if content_type is not None:
            headers[hdrs.CONTENT_TYPE] = content_type

        for _ in (1, 2):
            try:
                if use_token:
                    await self._ensure_access_token()
                    headers[hdrs.AUTHORIZATION] = f"Bearer {self._access_token}"
                async with session.request(
                    method,
                    url,
                    data=data,
                    timeout=client_timeout,
                    json=json,
                    headers=headers,
                    params=params,
                    ssl=False,
                ) as resp:
                    if resp.status != 401 or as_app:
                        yield resp
                        return
                    if use_token:
                        self._access_token = None
                        continue
                    # Over the Unix socket there is no token to refresh:
                    # Core does not accept the Supervisor user itself.
                    _LOGGER.error(
                        "Home Assistant rejected Supervisor credentials on %s", path
                    )
                    raise HomeAssistantAuthError
            except (TimeoutError, aiohttp.ClientError) as err:
                raise self._request_error(url, err, HomeAssistantAPIError) from err

        # Core still answered 401 with a freshly refreshed token.
        _LOGGER.error(
            "Home Assistant rejected Supervisor credentials on %s after token refresh",
            path,
        )
        raise HomeAssistantAuthError

    async def _get_json(self, path: str) -> dict[str, Any]:
        """Return Home Assistant get API."""
        async with self.make_request("get", path) as resp:
            if resp.status in (200, 201):
                return await resp.json()
            raise HomeAssistantAPIError(f"Home Assistant Core API return {resp.status}")

    async def get_config(self) -> dict[str, Any]:
        """Return Home Assistant config."""
        config = await self._get_json("api/config")
        if config is None or not isinstance(config, dict):
            raise HomeAssistantAPIError("No config received from Home Assistant API")
        return config

    async def get_core_state(self) -> dict[str, Any]:
        """Return Home Assistant core state."""
        state = await self._get_json("api/core/state")
        if state is None or not isinstance(state, dict):
            raise HomeAssistantAPIError("No state received from Home Assistant API")
        return state

    async def get_http_config(self) -> CoreHTTPConfig | None:
        """Return the live HTTP server configuration pulled from Core.

        Only available over the Unix socket on Core versions that provide the
        endpoint. Returns None when it cannot be fetched, in which case the
        values pushed by Core via the Supervisor options API remain in effect.
        """
        try:
            if not self.use_unix_socket:
                return None
            if not version_is_new_enough(
                self.sys_homeassistant.version, HTTP_CONFIG_MIN_VERSION
            ):
                return None
            data = await self._get_json("api/core/http_config")
        except HomeAssistantAPIError as err:
            _LOGGER.debug("Can't fetch Core HTTP config: %s", err)
            return None

        try:
            return CoreHTTPConfig(
                port=int(data["port"]),
                ssl=bool(data["ssl"]),
                ssl_peer_certificate=bool(data["ssl_peer_certificate"]),
                server_host=[str(host) for host in data["server_host"]],
            )
        except (KeyError, TypeError, ValueError) as err:
            _LOGGER.warning("Malformed Core HTTP config response: %s", err)
            return None

    async def _update_http_config(self) -> None:
        """Refresh the connection parameters from Core's HTTP config.

        Replaces relying on Core pushing port/SSL via the Supervisor options
        API, which races with Supervisor's own startup checks.
        """
        config = await self.get_http_config()
        homeassistant = self.sys_homeassistant
        # Reset to unknown when the config cannot be fetched (older Core, TCP
        # fallback), so reachability decisions never use another Core's binds.
        homeassistant.http_server_host = config.server_host if config else None
        if not config:
            return

        if (config.port, config.ssl) == (
            homeassistant.api_port,
            homeassistant.api_ssl,
        ):
            return

        _LOGGER.info(
            "Updating Core connection parameters from its HTTP config: port %s, ssl %s",
            config.port,
            config.ssl,
        )
        homeassistant.api_port = config.port
        homeassistant.api_ssl = config.ssl
        await homeassistant.save_data()

    async def get_api_state(self) -> APIState | None:
        """Return state of Home Assistant Core or None."""
        # Skip check on landingpage
        if (
            self.sys_homeassistant.version is None
            or self.sys_homeassistant.version == LANDINGPAGE
        ):
            return None

        # Check if API is up
        try:
            # get_core_state is available since 2023.8.0 and preferred
            # since it is significantly faster than get_config because
            # it does not require serializing the entire config
            if version_is_new_enough(
                self.sys_homeassistant.version, GET_CORE_STATE_MIN_VERSION
            ):
                data = await self.get_core_state()
            else:
                data = await self.get_config()

            if not self._core_connected:
                self._core_connected = True
                transport = (
                    f"Unix socket {self.core_socket_path}"
                    if self.use_unix_socket
                    else f"TCP {self.sys_homeassistant.api_url}"
                )
                _LOGGER.info("Connected to Core via %s", transport)
                await self._update_http_config()

            state = data.get("state", "RUNNING")
            # Recorder state was added in HA Core 2024.8
            recorder_state = data.get("recorder_state", {})
            migrating = recorder_state.get("migration_in_progress", False)
            live_migration = recorder_state.get("migration_is_live", False)
            return APIState(state, migrating and not live_migration)
        except HomeAssistantAPIError as err:
            _LOGGER.debug("Can't connect to Home Assistant API: %s", err)

        return None

    async def check_api_state(self) -> bool:
        """Return Home Assistant Core state if up."""
        if state := await self.get_api_state():
            return state.core_state == "RUNNING" or state.offline_db_migration
        return False
