"""Home Assistant control object."""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import logging
from typing import Any

import aiohttp
from aiohttp import hdrs
from awesomeversion import AwesomeVersion
from multidict import MultiMapping

from ..const import SOCKET_CORE, FeatureFlag
from ..coresys import CoreSys, CoreSysAttributes
from ..docker.const import ENV_CORE_API_SOCKET, ContainerState
from ..docker.monitor import DockerContainerStateEvent
from ..exceptions import HomeAssistantAPIError, HomeAssistantAuthError
from ..utils import version_is_new_enough
from .const import LANDINGPAGE
from .websocket import WSClient

_LOGGER: logging.Logger = logging.getLogger(__name__)

CORE_UNIX_SOCKET_MIN_VERSION: AwesomeVersion = AwesomeVersion(
    "2026.4.0.dev202603250907"
)
GET_CORE_STATE_MIN_VERSION: AwesomeVersion = AwesomeVersion("2023.8.0.dev20230720")


@dataclass(frozen=True)
class APIState:
    """Container for API state response."""

    core_state: str
    offline_db_migration: bool


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
        self._core_connected: bool = False

    @property
    def supports_unix_socket(self) -> bool:
        """Return True if the installed Core version supports Unix socket communication.

        Used to decide whether to configure the env var when starting Core.
        """
        return (
            self.sys_config.feature_flags.get(FeatureFlag.UNIX_SOCKET_CORE_API, False)
            and self.sys_homeassistant.version is not None
            and self.sys_homeassistant.version != LANDINGPAGE
            and version_is_new_enough(
                self.sys_homeassistant.version, CORE_UNIX_SOCKET_MIN_VERSION
            )
        )

    @property
    def use_unix_socket(self) -> bool:
        """Return True if the running Core container is configured for Unix socket.

        Checks both version support and that the container was actually started
        with the SUPERVISOR_CORE_API_SOCKET env var. This prevents failures
        during Supervisor upgrades where Core is still running with a container
        started by the old Supervisor.

        Requires container metadata to be available (via attach() or run()).
        Callers should ensure the container is running before using this.
        """
        if not self.supports_unix_socket:
            return False
        instance = self.sys_homeassistant.core.instance
        if not instance.attached:
            raise HomeAssistantAPIError(
                "Cannot determine Core connection mode: container metadata not available"
            )
        return any(
            env.startswith(f"{ENV_CORE_API_SOCKET}=")
            for env in instance.meta_config.get("Env", [])
        )

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
            self._unix_session = aiohttp.ClientSession(
                connector=aiohttp.UnixConnector(path=str(SOCKET_CORE))
            )
        return self._unix_session

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
        if event.state not in (ContainerState.STOPPED, ContainerState.FAILED):
            return

        self._core_connected = False
        if self._unix_session and not self._unix_session.closed:
            await self._unix_session.close()
            self._unix_session = None

    async def close(self) -> None:
        """Close the Unix socket session."""
        if self._unix_session and not self._unix_session.closed:
            await self._unix_session.close()
            self._unix_session = None

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

    async def connect_websocket(self) -> WSClient:
        """Connect a WebSocket to Core, handling auth as appropriate.

        For Unix socket connections, no authentication is needed.
        For TCP connections, handles token management with one retry
        on auth failure.

        Raises:
            HomeAssistantAPIError: On connection or auth failure.

        """
        if not await self.sys_homeassistant.core.instance.is_running():
            raise HomeAssistantAPIError("Core container is not running", _LOGGER.debug)

        if self.use_unix_socket:
            return await WSClient.connect(self.session, self.ws_url)

        for attempt in (1, 2):
            try:
                await self._ensure_access_token()
                assert self._access_token
                return await WSClient.connect_with_auth(
                    self.session, self.ws_url, self._access_token
                )
            except HomeAssistantAPIError:
                self._access_token = None
                if attempt == 2:
                    raise

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
            path: API path relative to Home Assistant base URL
            json: JSON data to send in request body
            content_type: Override content-type header
            data: Raw data to send in request body
            timeout: Request timeout in seconds
            params: URL query parameters
            headers: Additional HTTP headers

        Yields:
            aiohttp.ClientResponse: The HTTP response object

        Raises:
            HomeAssistantAPIError: When request cannot be completed due to
                network errors, timeouts, or connection failures

        """
        if not await self.sys_homeassistant.core.instance.is_running():
            raise HomeAssistantAPIError("Core container is not running", _LOGGER.debug)

        url = f"{self.api_url}/{path}"
        headers = headers or {}
        client_timeout = aiohttp.ClientTimeout(total=timeout)

        if content_type is not None:
            headers[hdrs.CONTENT_TYPE] = content_type

        for _ in (1, 2):
            try:
                if not self.use_unix_socket:
                    await self._ensure_access_token()
                    headers[hdrs.AUTHORIZATION] = f"Bearer {self._access_token}"
                async with self.session.request(
                    method,
                    url,
                    data=data,
                    timeout=client_timeout,
                    json=json,
                    headers=headers,
                    params=params,
                    ssl=False,
                ) as resp:
                    if resp.status == 401 and not self.use_unix_socket:
                        self._access_token = None
                        continue
                    yield resp
                    return
            except TimeoutError as err:
                _LOGGER.debug("Timeout on call %s.", url)
                raise HomeAssistantAPIError(str(err)) from err
            except aiohttp.ClientError as err:
                _LOGGER.debug("Error on call %s: %s", url, err)
                raise HomeAssistantAPIError(str(err)) from err

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
                    f"Unix socket {SOCKET_CORE}"
                    if self.use_unix_socket
                    else f"TCP {self.sys_homeassistant.api_url}"
                )
                _LOGGER.info("Connected to Core via %s", transport)

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

    async def check_frontend_available(self) -> bool:
        """Check if the frontend is accessible by fetching the root path.

        Caller should make sure that Home Assistant Core is running before
        calling this method.

        Returns:
            True if the frontend responds successfully, False otherwise.

        """
        try:
            async with self.make_request("get", "", timeout=30) as resp:
                # Frontend should return HTML content
                if resp.status == 200:
                    content_type = resp.headers.get(hdrs.CONTENT_TYPE, "")
                    if "text/html" in content_type:
                        _LOGGER.debug("Frontend is accessible and serving HTML")
                        return True
                    _LOGGER.warning(
                        "Frontend responded but with unexpected content type: %s",
                        content_type,
                    )
                    return False
                _LOGGER.warning("Frontend returned status %s", resp.status)
                return False
        except HomeAssistantAPIError as err:
            _LOGGER.debug("Cannot reach frontend: %s", err)
            return False
