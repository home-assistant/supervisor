"""Home Assistant Websocket API."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
from aiohttp.http_websocket import WSMsgType
from awesomeversion import AwesomeVersion

from ..const import ATTR_ACCESS_TOKEN, ATTR_DATA, ATTR_EVENT, ATTR_TYPE, ATTR_UPDATE_KEY
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import (
    HomeAssistantAPIError,
    HomeAssistantWSConnectionError,
    HomeAssistantWSError,
    HomeAssistantWSNotSupported,
)
from .const import CLOSING_STATES, MIN_VERSION, WSEvent, WSType

_LOGGER: logging.Logger = logging.getLogger(__name__)


class WSClient:
    """Home Assistant Websocket client."""

    def __init__(
        self,
        loop: asyncio.BaseEventLoop,
        ha_version: AwesomeVersion,
        client: aiohttp.ClientWebSocketResponse,
    ):
        """Initialise the WS client."""
        self.ha_version = ha_version
        self._client = client
        self._message_id: int = 0
        self._loop = loop
        self._futures: dict[int, asyncio.Future[dict]] = {}

    @property
    def connected(self) -> bool:
        """Return if we're currently connected."""
        return self._client is not None and not self._client.closed

    async def close(self) -> None:
        """Close down the client."""
        if not self._client.closed:
            await self._client.close()

    async def async_send_command(self, message: dict[str, Any]) -> dict | None:
        """Send a websocket message, and return the response."""
        self._message_id += 1
        message["id"] = self._message_id
        self._futures[message["id"]] = self._loop.create_future()
        _LOGGER.debug("Sending: %s", message)
        try:
            await self._client.send_json(message)
        except ConnectionError as err:
            raise HomeAssistantWSConnectionError(err) from err

        try:
            return await self._futures[message["id"]]
        finally:
            self._futures.pop(message["id"])

    async def start_listener(self) -> None:
        """Start listening to the websocket."""
        if not self.connected:
            raise HomeAssistantWSConnectionError("Not connected when start listening")

        try:
            while self.connected:
                await self._receive_json()
        except HomeAssistantWSConnectionError:
            pass

        except HomeAssistantWSError as err:
            _LOGGER.warning(err)

        finally:
            await self.close()

    async def _receive_json(self) -> None:
        """Receive json."""
        msg = await self._client.receive()
        _LOGGER.debug("Received: %s", msg)

        if msg.type in (
            WSMsgType.CLOSE,
            WSMsgType.CLOSED,
            WSMsgType.CLOSING,
            WSMsgType.ERROR,
        ):
            raise HomeAssistantWSConnectionError()

        if msg.type != WSMsgType.TEXT:
            raise HomeAssistantWSError(f"Received non-Text message: {msg.type}")

        try:
            data = msg.json()
        except ValueError as err:
            raise HomeAssistantWSError(f"Received invalid JSON - {msg}") from err

        if data["type"] == "result":
            if (future := self._futures.get(data["id"])) is None:
                return

            if data["success"]:
                future.set_result(data["result"])
                return

            _LOGGER.error("Unsuccessful websocket message - %s", data)

    @classmethod
    async def connect_with_auth(
        cls, session: aiohttp.ClientSession, loop, url: str, token: str
    ) -> "WSClient":
        """Create an authenticated websocket client."""
        try:
            client = await session.ws_connect(url, timeout=500)
        except aiohttp.client_exceptions.ClientConnectorError:
            raise HomeAssistantWSError("Can't connect") from None

        hello_message = await client.receive_json()

        await client.send_json({ATTR_TYPE: WSType.AUTH, ATTR_ACCESS_TOKEN: token})

        auth_ok_message = await client.receive_json()

        if auth_ok_message[ATTR_TYPE] != "auth_ok":
            raise HomeAssistantAPIError("AUTH NOT OK")

        return cls(loop, AwesomeVersion(hello_message["ha_version"]), client)


class HomeAssistantWebSocket(CoreSysAttributes):
    """Home Assistant Websocket API."""

    def __init__(self, coresys: CoreSys):
        """Initialize Home Assistant object."""
        self.coresys: CoreSys = coresys
        self._client: WSClient | None = None
        self._lock: asyncio.Lock = asyncio.Lock()

    async def _get_ws_client(self) -> WSClient:
        """Return a websocket client."""
        async with self._lock:
            if self._client is not None and self._client.connected:
                return self._client

            await self.sys_homeassistant.api.ensure_access_token()
            client = await WSClient.connect_with_auth(
                self.sys_websession,
                self.sys_loop,
                self.sys_homeassistant.ws_url,
                self.sys_homeassistant.api.access_token,
            )

            self.sys_create_task(client.start_listener())
            return client

    async def async_send_command(self, message: dict[str, Any]) -> dict[str, Any]:
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

        if not self._client.connected:
            self._client = await self._get_ws_client()

        message_type = message.get("type")

        if (
            message_type is not None
            and message_type in MIN_VERSION
            and self._client.ha_version < MIN_VERSION[message_type]
        ):
            _LOGGER.info(
                "WebSocket command %s is not supported until core-%s. Ignoring WebSocket message.",
                message_type,
                MIN_VERSION[message_type],
            )
            return

        try:
            return await self._client.async_send_command(message)
        except HomeAssistantWSError:
            await self._client.close()
            self._client = None

    async def async_supervisor_update_event(
        self,
        key: str,
        data: dict[str, Any] | None = None,
    ) -> None:
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

    def supervisor_update_event(
        self,
        key: str,
        data: dict[str, Any] | None = None,
    ) -> None:
        """Send a supervisor/event command."""
        if self.sys_core.state in CLOSING_STATES:
            return
        self.sys_create_task(self.async_supervisor_update_event(key, data))

    def send_command(self, message: dict[str, Any]) -> None:
        """Send a supervisor/event command."""
        if self.sys_core.state in CLOSING_STATES:
            return
        self.sys_create_task(self.async_send_command(message))
