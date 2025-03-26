"""Utils for Home Assistant Proxy."""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import logging

import aiohttp
from aiohttp import WSMessageTypeError, web
from aiohttp.client_exceptions import ClientConnectorError
from aiohttp.client_ws import ClientWebSocketResponse
from aiohttp.hdrs import AUTHORIZATION, CONTENT_TYPE
from aiohttp.http import WSMessage
from aiohttp.http_websocket import WSMsgType
from aiohttp.web_exceptions import HTTPBadGateway, HTTPUnauthorized

from ..coresys import CoreSysAttributes
from ..exceptions import APIError, HomeAssistantAPIError, HomeAssistantAuthError
from ..utils.json import json_dumps

_LOGGER: logging.Logger = logging.getLogger(__name__)


FORWARD_HEADERS = ("X-Speech-Content",)
HEADER_HA_ACCESS = "X-Ha-Access"

# Maximum message size for websocket messages from Home Assistant.
# Since these are coming from core we want the largest possible size
# that is not likely to cause a memory problem as most modern browsers
# support large messages.
# https://github.com/home-assistant/supervisor/issues/4392
MAX_MESSAGE_SIZE_FROM_CORE = 64 * 1024 * 1024


class APIProxy(CoreSysAttributes):
    """API Proxy for Home Assistant."""

    def _check_access(self, request: web.Request):
        """Check the Supervisor token."""
        if AUTHORIZATION in request.headers:
            bearer = request.headers[AUTHORIZATION]
            supervisor_token = bearer.split(" ")[-1]
        else:
            supervisor_token = request.headers.get(HEADER_HA_ACCESS, "")

        addon = self.sys_addons.from_token(supervisor_token)
        if not addon:
            _LOGGER.warning("Unknown Home Assistant API access!")
        elif not addon.access_homeassistant_api:
            _LOGGER.warning("Not permitted API access: %s", addon.slug)
        else:
            _LOGGER.debug("%s access from %s", request.path, addon.slug)
            return

        raise HTTPUnauthorized()

    @asynccontextmanager
    async def _api_client(
        self, request: web.Request, path: str, timeout: int | None = 300
    ) -> AsyncIterator[aiohttp.ClientResponse]:
        """Return a client request with proxy origin for Home Assistant."""
        try:
            async with self.sys_homeassistant.api.make_request(
                request.method.lower(),
                f"api/{path}",
                headers={
                    name: value
                    for name, value in request.headers.items()
                    if name in FORWARD_HEADERS
                },
                content_type=request.content_type,
                data=request.content,
                timeout=timeout,
                params=request.query,
            ) as resp:
                yield resp
                return

        except HomeAssistantAuthError:
            _LOGGER.error("Authenticate error on API for request %s", path)
        except HomeAssistantAPIError:
            _LOGGER.error("Error on API for request %s", path)
        except aiohttp.ClientError as err:
            _LOGGER.error("Client error on API %s request %s", path, err)
        except TimeoutError:
            _LOGGER.error("Client timeout error on API request %s", path)

        raise HTTPBadGateway()

    async def stream(self, request: web.Request):
        """Proxy HomeAssistant EventStream Requests."""
        self._check_access(request)
        if not await self.sys_homeassistant.api.check_api_state():
            raise HTTPBadGateway()

        _LOGGER.info("Home Assistant EventStream start")
        async with self._api_client(request, "stream", timeout=None) as client:
            response = web.StreamResponse()
            response.content_type = request.headers.get(CONTENT_TYPE, "")
            try:
                response.headers["X-Accel-Buffering"] = "no"
                await response.prepare(request)
                async for data in client.content:
                    await response.write(data)

            except (aiohttp.ClientError, aiohttp.ClientPayloadError):
                pass

            _LOGGER.info("Home Assistant EventStream close")
            return response

    async def api(self, request: web.Request):
        """Proxy Home Assistant API Requests."""
        self._check_access(request)
        if not await self.sys_homeassistant.api.check_api_state():
            raise HTTPBadGateway()

        # Normal request
        path = request.match_info["path"]
        async with self._api_client(request, path) as client:
            data = await client.read()
            return web.Response(
                body=data, status=client.status, content_type=client.content_type
            )

    async def _websocket_client(self) -> ClientWebSocketResponse:
        """Initialize a WebSocket API connection."""
        url = f"{self.sys_homeassistant.api_url}/api/websocket"

        try:
            client = await self.sys_websession.ws_connect(
                url, heartbeat=30, ssl=False, max_msg_size=MAX_MESSAGE_SIZE_FROM_CORE
            )

            # Handle authentication
            data = await client.receive_json()

            if data.get("type") == "auth_ok":
                return client

            if data.get("type") != "auth_required":
                # Invalid protocol
                raise APIError(
                    f"Got unexpected response from Home Assistant WebSocket: {data}",
                    _LOGGER.error,
                )

            # Auth session
            await self.sys_homeassistant.api.ensure_access_token()
            await client.send_json(
                {
                    "type": "auth",
                    "access_token": self.sys_homeassistant.api.access_token,
                },
                dumps=json_dumps,
            )

            data = await client.receive_json()

            if data.get("type") == "auth_ok":
                return client

            # Renew the Token is invalid
            if (
                data.get("type") == "invalid_auth"
                and self.sys_homeassistant.refresh_token
            ):
                self.sys_homeassistant.api.access_token = None
                return await self._websocket_client()

            raise HomeAssistantAuthError()

        except (RuntimeError, ValueError, TypeError, ClientConnectorError) as err:
            _LOGGER.error("Client error on WebSocket API %s.", err)
        except HomeAssistantAuthError:
            _LOGGER.error("Failed authentication to Home Assistant WebSocket")

        raise APIError()

    async def _proxy_message(
        self,
        read_task: asyncio.Task,
        target: web.WebSocketResponse | ClientWebSocketResponse,
    ) -> None:
        """Proxy a message from client to server or vice versa."""
        msg: WSMessage = read_task.result()
        match msg.type:
            case WSMsgType.TEXT:
                await target.send_str(msg.data)
            case WSMsgType.BINARY:
                await target.send_bytes(msg.data)
            case WSMsgType.CLOSE:
                _LOGGER.debug("Received close message from WebSocket.")
                await target.close()
            case _:
                raise TypeError(
                    f"Cannot proxy websocket message of unsupported type: {msg.type}"
                )

    async def websocket(self, request: web.Request):
        """Initialize a WebSocket API connection."""
        if not await self.sys_homeassistant.api.check_api_state():
            raise HTTPBadGateway()
        _LOGGER.info("Home Assistant WebSocket API request initialize")

        # init server
        server = web.WebSocketResponse(heartbeat=30)
        await server.prepare(request)
        addon_name = None

        # handle authentication
        try:
            await server.send_json(
                {"type": "auth_required", "ha_version": self.sys_homeassistant.version},
                dumps=json_dumps,
            )

            # Check API access, wait up to 10s just like _async_handle_auth_phase in Core
            response = await server.receive_json(timeout=10)
            supervisor_token = response.get("api_password") or response.get(
                "access_token"
            )
            addon = self.sys_addons.from_token(supervisor_token)

            if not addon or not addon.access_homeassistant_api:
                _LOGGER.warning("Unauthorized WebSocket access!")
                await server.send_json(
                    {"type": "auth_invalid", "message": "Invalid access"},
                    dumps=json_dumps,
                )
                return server

            addon_name = addon.slug
            _LOGGER.info("WebSocket access from %s", addon_name)

            await server.send_json(
                {"type": "auth_ok", "ha_version": self.sys_homeassistant.version},
                dumps=json_dumps,
            )
        except TimeoutError:
            _LOGGER.error("Timeout during authentication for WebSocket API")
            return server
        except WSMessageTypeError as err:
            _LOGGER.error(
                "Unexpected message during authentication for WebSocket API: %s", err
            )
            return server
        except (RuntimeError, ValueError) as err:
            _LOGGER.error("Can't initialize handshake: %s", err)
            return server

        # init connection to hass
        try:
            client = await self._websocket_client()
        except APIError:
            return server

        _LOGGER.info("Home Assistant WebSocket API request running")
        try:
            client_read: asyncio.Task | None = None
            server_read: asyncio.Task | None = None
            while not server.closed and not client.closed:
                if not client_read:
                    client_read = self.sys_create_task(client.receive())
                if not server_read:
                    server_read = self.sys_create_task(server.receive())

                # wait until data need to be processed
                await asyncio.wait(
                    [client_read, server_read], return_when=asyncio.FIRST_COMPLETED
                )

                # server
                if server_read.done() and not client.closed:
                    await self._proxy_message(server_read, client)
                    server_read = None

                # client
                if client_read.done() and not server.closed:
                    await self._proxy_message(client_read, server)
                    client_read = None

        except asyncio.CancelledError:
            pass

        except (RuntimeError, ConnectionError, TypeError) as err:
            _LOGGER.info("Home Assistant WebSocket API error: %s", err)

        finally:
            if client_read and not client_read.done():
                client_read.cancel()
            if server_read and not server_read.done():
                server_read.cancel()

            # close connections
            if not client.closed:
                await client.close()
            if not server.closed:
                await server.close()

        _LOGGER.info("Home Assistant WebSocket API for %s closed", addon_name)
        return server
