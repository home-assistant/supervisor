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

from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import HomeAssistantAPIError, HomeAssistantAuthError
from ..utils import version_is_new_enough
from .const import LANDINGPAGE

_LOGGER: logging.Logger = logging.getLogger(__name__)

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
        self.access_token: str | None = None
        self._access_token_expires: datetime | None = None
        self._token_lock: asyncio.Lock = asyncio.Lock()

    async def ensure_access_token(self) -> None:
        """Ensure there is a valid access token.

        Raises:
            HomeAssistantAuthError: When we cannot get a valid token
            aiohttp.ClientError: On network or connection errors
            TimeoutError: On request timeouts

        """
        # Fast path check without lock (avoid unnecessary locking
        # for the majority of calls).
        if (
            self.access_token
            and self._access_token_expires
            and self._access_token_expires > datetime.now(tz=UTC)
        ):
            return

        async with self._token_lock:
            # Double-check after acquiring lock (avoid race condition)
            if (
                self.access_token
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
                self.access_token = tokens["access_token"]
                self._access_token_expires = datetime.now(tz=UTC) + timedelta(
                    seconds=tokens["expires_in"]
                )

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
        """Async context manager to make authenticated requests to Home Assistant API.

        This context manager handles authentication token management automatically,
        including token refresh on 401 responses. It yields the HTTP response
        for the caller to handle.

        Error Handling:
        - HTTP error status codes (4xx, 5xx) are preserved in the response
        - Authentication is handled transparently with one retry on 401
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
        url = f"{self.sys_homeassistant.api_url}/{path}"
        headers = headers or {}

        # Passthrough content type
        if content_type is not None:
            headers[hdrs.CONTENT_TYPE] = content_type

        for _ in (1, 2):
            try:
                await self.ensure_access_token()
                headers[hdrs.AUTHORIZATION] = f"Bearer {self.access_token}"
                async with getattr(self.sys_websession, method)(
                    url,
                    data=data,
                    timeout=timeout,
                    json=json,
                    headers=headers,
                    params=params,
                    ssl=False,
                ) as resp:
                    # Access token expired
                    if resp.status == 401:
                        self.access_token = None
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
        return await self._get_json("api/config")

    async def get_core_state(self) -> dict[str, Any]:
        """Return Home Assistant core state."""
        return await self._get_json("api/core/state")

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
            # Older versions of home assistant does not expose the state
            if data:
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
