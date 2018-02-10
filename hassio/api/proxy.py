"""Utils for HomeAssistant Proxy."""
import asyncio
import logging

import aiohttp
from aiohttp import web
from aiohttp.web_exceptions import HTTPBadGateway, HTTPInternalServerError
from aiohttp.hdrs import CONTENT_TYPE
import async_timeout

from ..const import HEADER_HA_ACCESS
from ..coresys import CoreSysAttributes

_LOGGER = logging.getLogger(__name__)


class APIProxy(CoreSysAttributes):
    """API Proxy for Home-Assistant."""

    def _check_access(self, request):
        """Check the Hass.io token."""
        hassio_token = request.headers.get(HEADER_HA_ACCESS)
        addon = self._addons.from_uuid(hassio_token)

        if not addon:
            _LOGGER.warning("Unknown Home-Assistant API access!")
        else:
            _LOGGER.info("%s access from %s", request.path, addon.slug)

    async def _api_client(self, request, path, timeout=300):
        """Return a client request with proxy origin for Home-Assistant."""
        url = f"{self._homeassistant.api_url}/api/{path}"

        try:
            data = None
            headers = {}
            method = getattr(self._websession_ssl, request.method.lower())
            params = request.query or None

            # read data
            with async_timeout.timeout(30, loop=self._loop):
                data = await request.read()

            if data:
                headers.update({CONTENT_TYPE: request.content_type})

            # need api password?
            if self._homeassistant.api_password:
                headers = {HEADER_HA_ACCESS: self._homeassistant.api_password}

            # reset headers
            if not headers:
                headers = None

            client = await method(
                url, data=data, headers=headers, timeout=timeout,
                params=params
            )

            return client

        except aiohttp.ClientError as err:
            _LOGGER.error("Client error on API %s request %s.", path, err)

        except asyncio.TimeoutError:
            _LOGGER.error("Client timeout error on API request %s.", path)

        raise HTTPBadGateway()

    async def stream(self, request):
        """Proxy HomeAssistant EventStream Requests."""
        self._check_access(request)

        _LOGGER.info("Home-Assistant EventStream start")
        client = await self._api_client(request, 'stream', timeout=None)

        response = web.StreamResponse()
        response.content_type = request.headers.get(CONTENT_TYPE)
        try:
            await response.prepare(request)
            while True:
                data = await client.content.read(10)
                if not data:
                    await response.write_eof()
                    break
                response.write(data)

        except aiohttp.ClientError:
            await response.write_eof()

        except asyncio.CancelledError:
            pass

        finally:
            client.close()
            _LOGGER.info("Home-Assistant EventStream close")

        return response

    async def api(self, request):
        """Proxy HomeAssistant API Requests."""
        self._check_access(request)

        # Normal request
        path = request.match_info.get('path', '')
        client = await self._api_client(request, path)

        data = await client.read()
        return web.Response(
            body=data,
            status=client.status,
            content_type=client.content_type
        )

    async def _websocket_client(self):
        """Initialize a websocket api connection."""
        url = f"{self._homeassistant.api_url}/api/websocket"

        try:
            client = await self._websession_ssl.ws_connect(
                url, heartbeat=60, verify_ssl=False)

            # handle authentication
            for _ in range(2):
                data = await client.receive_json()
                if data.get('type') == 'auth_ok':
                    return client
                elif data.get('type') == 'auth_required':
                    await client.send_json({
                        'type': 'auth',
                        'api_password': self._homeassistant.api_password,
                    })

            _LOGGER.error("Authentication to Home-Assistant websocket")

        except (aiohttp.ClientError, RuntimeError) as err:
            _LOGGER.error("Client error on websocket API %s.", err)

        raise HTTPBadGateway()

    async def websocket(self, request):
        """Initialize a websocket api connection."""
        _LOGGER.info("Home-Assistant Websocket API request initialze")

        # init server
        server = web.WebSocketResponse(heartbeat=60)
        await server.prepare(request)

        # handle authentication
        try:
            await server.send_json({
                'type': 'auth_required',
                'ha_version': self._homeassistant.version,
            })

            # Check API access
            response = await server.receive_json()
            hassio_token = response.get('api_password')
            addon = self._addons.from_uuid(hassio_token)

            if not addon:
                _LOGGER.waring("Unauthorized websocket access!")
            else:
                _LOGGER.info("Websocket access from %s", addon.slug)

            await server.send_json({
                'type': 'auth_ok',
                'ha_version': self._homeassistant.version,
            })
        except (RuntimeError, ValueError) as err:
            _LOGGER.error("Can't initialize handshake: %s", err)
            raise HTTPInternalServerError() from None

        # init connection to hass
        client = await self._websocket_client()

        _LOGGER.info("Home-Assistant Websocket API request running")
        try:
            client_read = None
            server_read = None
            while not server.closed and not client.closed:
                if not client_read:
                    client_read = asyncio.ensure_future(
                        client.receive_str(), loop=self._loop)
                if not server_read:
                    server_read = asyncio.ensure_future(
                        server.receive_str(), loop=self._loop)

                # wait until data need to be processed
                await asyncio.wait(
                    [client_read, server_read],
                    loop=self._loop, return_when=asyncio.FIRST_COMPLETED
                )

                # server
                if server_read.done() and not client.closed:
                    server_read.exception()
                    await client.send_str(server_read.result())
                    server_read = None

                # client
                if client_read.done() and not server.closed:
                    client_read.exception()
                    await server.send_str(client_read.result())
                    client_read = None

        except asyncio.CancelledError:
            pass

        except RuntimeError as err:
            _LOGGER.info("Home-Assistant Websocket API error: %s", err)

        finally:
            if client_read:
                client_read.cancel()
            if server_read:
                server_read.cancel()

            # close connections
            await client.close()
            await server.close()

        _LOGGER.info("Home-Assistant Websocket API connection is closed")
        return server
