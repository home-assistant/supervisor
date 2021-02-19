"""Home Assistant Websocket API."""
import logging
from typing import Any, Dict, Optional

import aiohttp
from awesomeversion import AwesomeVersion

from ..const import CoreState
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import (
    HomeAssistantAPIError,
    HomeAssistantWSError,
    HomeAssistantWSNotSupported,
)

_LOGGER: logging.Logger = logging.getLogger(__name__)

CLOSING_STATES = [
    CoreState.SHUTDOWN,
    CoreState.STOPPING,
    CoreState.CLOSE,
]

MIN_VERSION = "2021.2.4"


class WSClient:
    """Home Assistant Websocket client."""

    def __init__(
        self, ha_version: AwesomeVersion, client: aiohttp.ClientWebSocketResponse
    ):
        """Initialise the WS client."""
        self.ha_version = ha_version
        self.client = client
        self.message_id = 0

    async def async_send_command(self, message: Dict[str, Any]):
        """Send a websocket command."""
        self.message_id += 1
        message["id"] = self.message_id

        _LOGGER.debug("Sending: %s", message)
        try:
            await self.client.send_json(message)
        except HomeAssistantWSNotSupported:
            return

        response = await self.client.receive_json()

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
            await client.send_json({"type": "auth", "access_token": token})
        except HomeAssistantWSNotSupported:
            return

        auth_ok_message = await client.receive_json()

        if auth_ok_message["type"] != "auth_ok":
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
        if client.ha_version < MIN_VERSION:
            _LOGGER.warning("No WebSocket support untill core-%s", MIN_VERSION)

        return client

    async def async_send_command(self, message: Dict[str, Any]):
        """Send a command with the WS client."""
        if self.sys_core.state in CLOSING_STATES:
            raise HomeAssistantWSNotSupported(
                f"Can't execute in a ${self.sys_core.state} state"
            )
        if not self._client:
            self._client = await self._get_ws_client()

        if self._client.ha_version < MIN_VERSION:
            raise HomeAssistantWSNotSupported

        try:
            return await self._client.async_send_command(message)
        except HomeAssistantAPIError as err:
            raise HomeAssistantWSError from err

    async def async_supervisor_update_event(self, key: str, data: Dict[str, Any]):
        """Send a supervisor/event command."""
        try:
            await self.async_send_command(
                {
                    "type": "supervisor/event",
                    "data": {
                        "event": "supervisor-update",
                        "update_key": key,
                        "data": data,
                    },
                }
            )
        except HomeAssistantWSNotSupported:
            pass
        except HomeAssistantWSError as err:
            _LOGGER.error(err)
