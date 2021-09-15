"""Home Assistant control object."""
import asyncio
from contextlib import asynccontextmanager, suppress
from datetime import datetime, timedelta
import logging
from typing import Any, AsyncContextManager, Dict, Optional

import aiohttp
from aiohttp import hdrs

from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import HomeAssistantAPIError, HomeAssistantAuthError
from ..jobs.const import JobExecutionLimit
from ..jobs.decorator import Job
from ..utils import check_port
from .const import LANDINGPAGE

_LOGGER: logging.Logger = logging.getLogger(__name__)


class HomeAssistantAPI(CoreSysAttributes):
    """Home Assistant core object for handle it."""

    def __init__(self, coresys: CoreSys):
        """Initialize Home Assistant object."""
        self.coresys: CoreSys = coresys

        # We don't persist access tokens. Instead we fetch new ones when needed
        self.access_token: Optional[str] = None
        self._access_token_expires: Optional[datetime] = None

    @Job(limit=JobExecutionLimit.SINGLE_WAIT)
    async def ensure_access_token(self) -> None:
        """Ensure there is an access token."""
        if (
            self.access_token is not None
            and self._access_token_expires > datetime.utcnow()
        ):
            return

        with suppress(asyncio.TimeoutError, aiohttp.ClientError):
            async with self.sys_websession.post(
                f"{self.sys_homeassistant.api_url}/auth/token",
                timeout=30,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": self.sys_homeassistant.refresh_token,
                },
                ssl=False,
            ) as resp:
                if resp.status != 200:
                    _LOGGER.error("Can't update Home Assistant access token!")
                    raise HomeAssistantAuthError()

                _LOGGER.info("Updated Home Assistant API token")
                tokens = await resp.json()
                self.access_token = tokens["access_token"]
                self._access_token_expires = datetime.utcnow() + timedelta(
                    seconds=tokens["expires_in"]
                )

    @asynccontextmanager
    async def make_request(
        self,
        method: str,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        content_type: Optional[str] = None,
        data: Any = None,
        timeout: int = 30,
        params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> AsyncContextManager[aiohttp.ClientResponse]:
        """Async context manager to make a request with right auth."""
        url = f"{self.sys_homeassistant.api_url}/{path}"
        headers = headers or {}

        # Passthrough content type
        if content_type is not None:
            headers[hdrs.CONTENT_TYPE] = content_type

        for _ in (1, 2):
            await self.ensure_access_token()
            headers[hdrs.AUTHORIZATION] = f"Bearer {self.access_token}"

            try:
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
            except (asyncio.TimeoutError, aiohttp.ClientError) as err:
                _LOGGER.error("Error on call %s: %s", url, err)
                break

        raise HomeAssistantAPIError()

    async def get_config(self) -> Optional[Dict[str, Any]]:
        """Return Home Assistant config."""
        async with self.make_request("get", "api/config") as resp:
            if resp.status in (200, 201):
                return await resp.json()
            else:
                _LOGGER.debug("Home Assistant API return: %d", resp.status)
        return None

    async def check_api_state(self) -> bool:
        """Return True if Home Assistant up and running."""
        # Skip check on landingpage
        if (
            self.sys_homeassistant.version is None
            or self.sys_homeassistant.version == LANDINGPAGE
        ):
            return False

        # Check if port is up
        if not await self.sys_run_in_executor(
            check_port,
            self.sys_homeassistant.ip_address,
            self.sys_homeassistant.api_port,
        ):
            return False

        # Check if API is up
        with suppress(HomeAssistantAPIError):
            data = await self.get_config()
            if data and data.get("state") == "RUNNING":
                return True
        return False
