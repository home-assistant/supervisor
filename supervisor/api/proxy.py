"""Utils for Home Assistant Proxy."""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import logging

import aiohttp
from aiohttp import WSCloseCode, WSMessageTypeError, web
from aiohttp.client_exceptions import ClientConnectorError
from aiohttp.client_ws import ClientWebSocketResponse
from aiohttp.hdrs import AUTHORIZATION, CONTENT_TYPE
from aiohttp.http_websocket import WSMsgType
from aiohttp.web_exceptions import HTTPBadGateway, HTTPUnauthorized

from supervisor.utils.logging import AddonLoggerAdapter

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
        path = request.match_info.get("path", "")
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
        source: web.WebSocketResponse | ClientWebSocketResponse,
        target: web.WebSocketResponse | ClientWebSocketResponse,
        logger: AddonLoggerAdapter,
    ) -> None:
        """Proxy a message from client to server or vice versa."""
        while not source.closed and not target.closed:
            msg = await source.receive()
            match msg.type:
                case WSMsgType.TEXT:
                    await target.send_str(msg.data)
                case WSMsgType.BINARY:
                    await target.send_bytes(msg.data)
                case WSMsgType.CLOSE | WSMsgType.CLOSED:
                    logger.debug(
                        "Received WebSocket message type %r from %s.",
                        msg.type,
                        "add-on" if type(source) is web.WebSocketResponse else "Core",
                    )
                    await target.close()
                case WSMsgType.CLOSING:
                    pass
                case WSMsgType.ERROR:
                    logger.warning(
                        "Error WebSocket message received while proxying: %r", msg.data
                    )
                    await target.close(
                        code=source.close_code or WSCloseCode.INTERNAL_ERROR
                    )
                case _:
                    logger.warning(
                        "Cannot proxy WebSocket message of unsupported type: %r",
                        msg.type,
                    )
                    await source.close()
                    await target.close()

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

        logger = AddonLoggerAdapter(_LOGGER, {"addon_name": addon_name})
        logger.info("Home Assistant WebSocket API proxy running")

        client_task = self.sys_create_task(self._proxy_message(client, server, logger))
        server_task = self.sys_create_task(self._proxy_message(server, client, logger))

        # Typically, this will return with an empty pending set. However, if one of
        # the directions has an exception, make sure to close both connections and
        # wait for the other proxy task to exit gracefully. Using this over try-except
        # handling makes it easier to wait for the other direction to complete.
        _, pending = await asyncio.wait(
            (client_task, server_task), return_when=asyncio.FIRST_EXCEPTION
        )

        if not client.closed:
            await client.close()
        if not server.closed:
            await server.close()

        if pending:
            _, pending = await asyncio.wait(
                pending, timeout=10, return_when=asyncio.ALL_COMPLETED
            )
            for task in pending:
                task.cancel()
                logger.critical("WebSocket proxy task: %s did not end gracefully", task)

        logger.info("Home Assistant WebSocket API closed")
        return server
