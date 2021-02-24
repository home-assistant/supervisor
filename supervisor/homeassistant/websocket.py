"""Home Assistant Websocket API."""
import asyncio
import logging
from typing import Any, Dict, Optional

import aiohttp
from awesomeversion import AwesomeVersion

from ..const import ATTR_ACCESS_TOKEN, ATTR_DATA, ATTR_EVENT, ATTR_TYPE, ATTR_UPDATE_KEY
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import (
    HomeAssistantAPIError,
    HomeAssistantWSError,
    HomeAssistantWSNotSupported,
)
from .const import CLOSING_STATES, MIN_VERSION, WSEvent, WSType

_LOGGER: logging.Logger = logging.getLogger(__name__)


class WSClient:
    """Home Assistant Websocket client."""

    def __init__(
        self, ha_version: AwesomeVersion, client: aiohttp.ClientWebSocketResponse
    ):
        """Initialise the WS client."""
        self.ha_version: AwesomeVersion = ha_version
        self.client: aiohttp.ClientWebSocketResponse = client
        self.message_id: int = 0
        self._lock: asyncio.Lock = asyncio.Lock()

    async def async_send_command(self, message: Dict[str, Any]):
        """Send a websocket command."""
        async with self._lock:
            self.message_id += 1
            message["id"] = self.message_id

            _LOGGER.debug("Sending: %s", message)
            try:
                await self.client.send_json(message)
            except ConnectionError:
                return

            try:
                response = await self.client.receive_json()
            except ConnectionError:
                return

            _LOGGER.debug("Received: %s", response)

            if response["success"]:
                return response["result"]

            raise HomeAssistantWSError(response)

    @classmethod
    async def connect_with_auth(
        cls, session: aiohttp.ClientSession, url: str, token: str
    ) -> "WSClient":
        """Create an authenticated websocket client."""
        try:
            client = await session.ws_connect(url)
        except aiohttp.client_exceptions.ClientConnectorError:
            raise HomeAssistantWSError("Can't connect") from None

        hello_message = await client.receive_json()

        try:
            await client.send_json({ATTR_TYPE: WSType.AUTH, ATTR_ACCESS_TOKEN: token})
        except HomeAssistantWSNotSupported:
            return

        auth_ok_message = await client.receive_json()

        if auth_ok_message[ATTR_TYPE] != "auth_ok":
            raise HomeAssistantAPIError("AUTH NOT OK")

        return cls(AwesomeVersion(hello_message["ha_version"]), client)


class HomeAssistantWebSocket(CoreSysAttributes):
    """Home Assistant Websocket API."""

    def __init__(self, coresys: CoreSys):
        """Initialize Home Assistant object."""
        self.coresys: CoreSys = coresys
        self._client: Optional[WSClient] = None

    async def _get_ws_client(self) -> WSClient:
        """Return a websocket client."""
        await self.sys_homeassistant.api.ensure_access_token()
        client = await WSClient.connect_with_auth(
            self.sys_websession_ssl,
            f"{self.sys_homeassistant.api_url}/api/websocket",
            self.sys_homeassistant.api.access_token,
        )

        return client

    async def async_send_command(self, message: Dict[str, Any]):
        """Send a command with the WS client."""
        if self.sys_core.state in CLOSING_STATES:
            raise HomeAssistantWSNotSupported(
                f"Can't execute in a ${self.sys_core.state} state"
            )
        if not await self.sys_homeassistant.api.check_api_state():
            # No core access, don't try.
            return

        if not self._client:
            self._client = await self._get_ws_client()

        message_type = message.get("type")

        if (
            message_type is not None
            and message_type in MIN_VERSION
            and self._client.ha_version < MIN_VERSION[message_type]
        ):
            _LOGGER.info(
                "WebSocket command %s is not supported untill core-%s. Ignoring WebSocket message.",
                message_type,
                MIN_VERSION[message_type],
            )
            return

        try:
            return await self._client.async_send_command(message)
        except HomeAssistantAPIError as err:
            raise HomeAssistantWSError from err

    async def async_supervisor_update_event(
        self, key: str, data: Optional[Dict[str, Any]] = None
    ):
        """Send a supervisor/event command."""
        try:
            await self.async_send_command(
                {
                    ATTR_TYPE: WSType.SUPERVISOR_EVENT,
                    ATTR_DATA: {
                        ATTR_EVENT: WSEvent.SUPERVISOR_UPDATE,
                        ATTR_UPDATE_KEY: key,
                        ATTR_DATA: data or {},
                    },
                }
            )
        except HomeAssistantWSNotSupported:
            pass
        except HomeAssistantWSError as err:
            _LOGGER.error(err)

    def supervisor_update_event(self, key: str, data: Optional[Dict[str, Any]] = None):
        """Send a supervisor/event command."""
        if self.sys_core.state in CLOSING_STATES:
            return
        self.sys_create_task(self.async_supervisor_update_event(key, data))

    def send_command(self, message: Dict[str, Any]):
        """Send a supervisor/event command."""
        if self.sys_core.state in CLOSING_STATES:
            return
        self.sys_create_task(self.async_send_command(message))
