"""Home Assistant Websocket API."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, TypeVar

import aiohttp
from aiohttp.http_websocket import WSMsgType
from awesomeversion import AwesomeVersion

from ..const import (
    ATTR_ACCESS_TOKEN,
    ATTR_DATA,
    ATTR_EVENT,
    ATTR_SUPPORTED,
    ATTR_TYPE,
    ATTR_UPDATE_KEY,
    ATTR_VERSION,
    STARTING_STATES,
    BusEvent,
    CoreState,
)
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import (
    HomeAssistantAPIError,
    HomeAssistantWSConnectionError,
    HomeAssistantWSError,
)
from ..jobs import process_job_dict_for_legacy_compatibility
from ..utils.json import json_dumps
from .const import (
    CLOSING_STATES,
    DEFAULT_EVENT_VERSION,
    EVENT_VERSION_APP_JOB_NAMES,
    SUPPORTED_EVENT_VERSIONS,
    WSEvent,
    WSType,
)

_LOGGER: logging.Logger = logging.getLogger(__name__)

T = TypeVar("T")

# Maximum message size for WebSocket messages from Core. Matches the cap used
# by the ingress proxy; Supervisor's own control channel never gets close to
# this but shares the setting for simplicity. See issue #4392.
MAX_MESSAGE_SIZE_FROM_CORE = 64 * 1024 * 1024


def _map_job_event_to_legacy_names(message: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of a job event message using the legacy job name.

    Consumers of event version 1 expect the legacy job names. Messages other
    than job events pass through unchanged.
    """
    if (
        message.get(ATTR_TYPE) != WSType.SUPERVISOR_EVENT
        or not isinstance(data := message.get(ATTR_DATA), dict)
        or data.get(ATTR_EVENT) != WSEvent.JOB
        or not isinstance(job_data := data.get(ATTR_DATA), dict)
    ):
        return message

    return message | {
        ATTR_DATA: data
        | {ATTR_DATA: process_job_dict_for_legacy_compatibility(job_data)}
    }


class WSClient:
    """Home Assistant Websocket client."""

    def __init__(
        self,
        ha_version: AwesomeVersion,
        client: aiohttp.ClientWebSocketResponse,
    ):
        """Initialise the WS client."""
        self.ha_version = ha_version
        self.client = client
        self.event_version: int = DEFAULT_EVENT_VERSION
        self._message_id: int = 0
        self._futures: dict[int, asyncio.Future[T]] = {}  # type: ignore

    @property
    def connected(self) -> bool:
        """Return if we're currently connected."""
        return self.client is not None and not self.client.closed

    async def close(self) -> None:
        """Close down the client."""
        for future in self._futures.values():
            if not future.done():
                future.set_exception(
                    HomeAssistantWSConnectionError("Connection was closed")
                )

        if not self.client.closed:
            await self.client.close()

    async def async_send_command(self, message: dict[str, Any]) -> T:
        """Send a websocket message, and return the response."""
        self._message_id += 1
        message["id"] = self._message_id
        self._futures[message["id"]] = asyncio.get_running_loop().create_future()
        _LOGGER.debug("Sending: %s", message)
        try:
            await self.client.send_json(message, dumps=json_dumps)
        except ConnectionError as err:
            raise HomeAssistantWSConnectionError(str(err)) from err

        try:
            return await self._futures[message["id"]]
        finally:
            self._futures.pop(message["id"])

    async def negotiate_event_version(self) -> None:
        """Negotiate the supervisor event version with Core.

        Offers the supported versions to Core, which replies with the one it
        wants to receive. A Core without support for the command rejects it
        and the default version stays in use.

        Raises HomeAssistantWSConnectionError if the connection fails.
        """
        try:
            result: dict[str, Any] = await self.async_send_command(
                {
                    ATTR_TYPE: WSType.SUPERVISOR_EVENT_VERSION,
                    ATTR_SUPPORTED: sorted(SUPPORTED_EVENT_VERSIONS),
                }
            )
        except HomeAssistantWSConnectionError:
            raise
        except HomeAssistantWSError:
            _LOGGER.debug(
                "Core does not support event version negotiation, using version %s",
                self.event_version,
            )
            return

        version = result.get(ATTR_VERSION) if isinstance(result, dict) else None
        if version in SUPPORTED_EVENT_VERSIONS:
            self.event_version = version
        else:
            _LOGGER.warning(
                "Core requested unsupported event version %s, using version %s",
                version,
                self.event_version,
            )

    async def start_listener(self) -> None:
        """Start listening to the websocket."""
        if not self.connected:
            raise HomeAssistantWSConnectionError("Not connected when start listening")

        try:
            while self.connected:
                await self._receive_json()
        except HomeAssistantWSError:
            pass

        finally:
            await self.close()

    async def _receive_json(self) -> None:
        """Receive json."""
        msg = await self.client.receive()
        _LOGGER.debug("Received: %s", msg)

        if msg.type == WSMsgType.CLOSE:
            raise HomeAssistantWSConnectionError("Connection was closed", _LOGGER.debug)

        if msg.type in (
            WSMsgType.CLOSED,
            WSMsgType.CLOSING,
        ):
            raise HomeAssistantWSConnectionError(
                "Connection is closed", _LOGGER.warning
            )

        if msg.type == WSMsgType.ERROR:
            raise HomeAssistantWSError(f"WebSocket Error: {msg}", _LOGGER.error)

        if msg.type != WSMsgType.TEXT:
            raise HomeAssistantWSError(
                f"Received non-Text message: {msg.type}", _LOGGER.error
            )

        try:
            data = msg.json()
        except ValueError as err:
            raise HomeAssistantWSError(
                f"Received invalid JSON - {msg}", _LOGGER.error
            ) from err

        if data["type"] == "result":
            if (future := self._futures.get(data["id"])) is None:
                return

            if data["success"]:
                future.set_result(data["result"])
                return

            future.set_exception(
                HomeAssistantWSError(f"Unsuccessful websocket message - {data}")
            )

    @classmethod
    async def _ws_connect(
        cls,
        session: aiohttp.ClientSession,
        url: str,
    ) -> aiohttp.ClientWebSocketResponse:
        """Open a raw WebSocket connection to Core."""
        try:
            return await session.ws_connect(
                url, ssl=False, max_msg_size=MAX_MESSAGE_SIZE_FROM_CORE
            )
        except aiohttp.client_exceptions.ClientConnectorError:
            raise HomeAssistantWSConnectionError("Can't connect") from None

    @classmethod
    async def connect(
        cls,
        session: aiohttp.ClientSession,
        url: str,
    ) -> WSClient:
        """Connect via Unix socket (no auth exchange).

        Core authenticates the peer by the socket connection itself
        and sends auth_ok immediately.
        """
        client = await cls._ws_connect(session, url)
        try:
            first_message = await client.receive_json()

            if first_message[ATTR_TYPE] != "auth_ok":
                raise HomeAssistantAPIError(
                    f"Expected auth_ok on Unix socket, got {first_message[ATTR_TYPE]}"
                )

            return cls(AwesomeVersion(first_message["ha_version"]), client)
        except HomeAssistantAPIError:
            await client.close()
            raise
        except (
            KeyError,
            ValueError,
            TypeError,
            aiohttp.ClientError,
            TimeoutError,
        ) as err:
            await client.close()
            raise HomeAssistantWSConnectionError(
                f"Unexpected error during WebSocket handshake: {err}"
            ) from err

    @classmethod
    async def connect_with_auth(
        cls,
        session: aiohttp.ClientSession,
        url: str,
        token: str,
    ) -> WSClient:
        """Connect via TCP with token authentication.

        Expects auth_required from Core, sends the token, then expects auth_ok.
        The auth_required message also carries ha_version.
        """
        client = await cls._ws_connect(session, url)
        try:
            # auth_required message also carries ha_version
            first_message = await client.receive_json()

            if first_message[ATTR_TYPE] != "auth_required":
                raise HomeAssistantAPIError(
                    f"Expected auth_required, got {first_message[ATTR_TYPE]}"
                )

            await client.send_json(
                {ATTR_TYPE: WSType.AUTH, ATTR_ACCESS_TOKEN: token}, dumps=json_dumps
            )

            auth_ok_message = await client.receive_json()

            if auth_ok_message[ATTR_TYPE] != "auth_ok":
                raise HomeAssistantAPIError("AUTH NOT OK")

            return cls(AwesomeVersion(first_message["ha_version"]), client)
        except HomeAssistantAPIError:
            await client.close()
            raise
        except (
            KeyError,
            ValueError,
            TypeError,
            aiohttp.ClientError,
            TimeoutError,
        ) as err:
            await client.close()
            raise HomeAssistantWSConnectionError(
                f"Unexpected error during WebSocket handshake: {err}"
            ) from err


class HomeAssistantWebSocket(CoreSysAttributes):
    """Home Assistant Websocket API."""

    def __init__(self, coresys: CoreSys):
        """Initialize Home Assistant object."""
        self.coresys: CoreSys = coresys
        self.client: WSClient | None = None
        self._lock: asyncio.Lock = asyncio.Lock()
        self._queue: list[dict[str, Any]] = []

    async def _process_queue(self, reference: CoreState) -> None:
        """Process queue once supervisor is running."""
        if reference == CoreState.RUNNING:
            for msg in self._queue:
                await self._async_send_command(msg)

            self._queue.clear()

    async def _get_ws_client(self) -> WSClient:
        """Return a websocket client."""
        async with self._lock:
            if self.client is not None and self.client.connected:
                return self.client

            client = await self.sys_homeassistant.api.connect_websocket()

            self.sys_create_task(client.start_listener())
            await client.negotiate_event_version()
            return client

    async def _ensure_connected(self) -> None:
        """Ensure WebSocket connection is ready.

        Raises HomeAssistantWSConnectionError if unable to connect.
        Raises HomeAssistantAuthError if authentication with Core fails.
        """
        if self.sys_core.state in CLOSING_STATES:
            raise HomeAssistantWSConnectionError(
                "WebSocket not available, system is shutting down"
            )

        connected = self.client and self.client.connected
        # If we are already connected, we can avoid the check_api_state call
        # since it makes a new socket connection and we already have one.
        if not connected and not await self.sys_homeassistant.api.check_api_state():
            raise HomeAssistantWSConnectionError(
                "Can't connect to Home Assistant Core WebSocket, the API is not reachable"
            )

        if not self.client or not self.client.connected:
            self.client = await self._get_ws_client()

    async def load(self) -> None:
        """Set up queue processor after startup completes."""
        self.sys_bus.register_event(
            BusEvent.SUPERVISOR_STATE_CHANGE, self._process_queue
        )

    async def _async_send_command(self, message: dict[str, Any]) -> None:
        """Send a fire-and-forget command via WebSocket.

        Queues messages during startup. Silently handles connection errors.
        """
        if self.sys_core.state in STARTING_STATES:
            self._queue.append(message)
            _LOGGER.debug("Queuing message until startup has completed: %s", message)
            return

        try:
            await self._ensure_connected()
        except HomeAssistantWSError as err:
            _LOGGER.debug("Can't send WebSocket command: %s", err)
            return

        # _ensure_connected guarantees self.client is set
        assert self.client

        if self.client.event_version < EVENT_VERSION_APP_JOB_NAMES:
            message = _map_job_event_to_legacy_names(message)

        try:
            await self.client.async_send_command(message)
        except HomeAssistantWSConnectionError as err:
            _LOGGER.debug("Fire-and-forget WebSocket command failed: %s", err)
            if self.client:
                await self.client.close()
            self.client = None

    async def async_send_command(self, message: dict[str, Any]) -> T:
        """Send a command and return the response.

        Raises HomeAssistantWSError on WebSocket connection or communication failure.
        """
        await self._ensure_connected()
        # _ensure_connected guarantees self.client is set
        assert self.client
        try:
            return await self.client.async_send_command(message)
        except HomeAssistantWSConnectionError:
            if self.client:
                await self.client.close()
            self.client = None
            raise

    def send_command(self, message: dict[str, Any]) -> None:
        """Send a fire-and-forget command via WebSocket."""
        if self.sys_core.state in CLOSING_STATES:
            return
        self.sys_create_task(self._async_send_command(message))

    async def async_supervisor_event_custom(
        self, event: WSEvent, extra_data: dict[str, Any] | None = None
    ) -> None:
        """Send a supervisor/event message to Home Assistant with custom data."""
        try:
            await self._async_send_command(
                {
                    ATTR_TYPE: WSType.SUPERVISOR_EVENT,
                    ATTR_DATA: {
                        ATTR_EVENT: event,
                        **(extra_data or {}),
                    },
                }
            )
        except HomeAssistantWSError as err:
            _LOGGER.error("Could not send message to Home Assistant due to %s", err)

    def supervisor_event_custom(
        self, event: WSEvent, extra_data: dict[str, Any] | None = None
    ) -> None:
        """Send a supervisor/event message to Home Assistant with custom data."""
        if self.sys_core.state in CLOSING_STATES:
            return
        self.sys_create_task(self.async_supervisor_event_custom(event, extra_data))

    def supervisor_event(
        self, event: WSEvent, data: dict[str, Any] | None = None
    ) -> None:
        """Send a supervisor/event message to Home Assistant."""
        if self.sys_core.state in CLOSING_STATES:
            return
        self.sys_create_task(
            self.async_supervisor_event_custom(event, {ATTR_DATA: data or {}})
        )

    async def async_supervisor_update_event(
        self,
        key: str,
        data: dict[str, Any] | None = None,
    ) -> None:
        """Send an update supervisor/event message."""
        await self.async_supervisor_event_custom(
            WSEvent.SUPERVISOR_UPDATE,
            {
                ATTR_UPDATE_KEY: key,
                ATTR_DATA: data or {},
            },
        )

    def supervisor_update_event(
        self,
        key: str,
        data: dict[str, Any] | None = None,
    ) -> None:
        """Send an update supervisor/event message."""
        if self.sys_core.state in CLOSING_STATES:
            return
        self.sys_create_task(self.async_supervisor_update_event(key, data))
