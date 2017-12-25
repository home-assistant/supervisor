"""Utils for HomeAssistant Proxy."""
import asyncio
import logging

import aiohttp
from aiohttp import web
from aiohttp.web_exceptions import HTTPBadGateway
from aiohttp.hdrs import CONTENT_TYPE
import async_timeout

from ..const import HEADER_HA_ACCESS

_LOGGER = logging.getLogger(__name__)


class APIProxy(object):
    """API Proxy for Home-Assistant."""

    def __init__(self, loop, homeassistant, websession):
        """Initialize api proxy."""
        self.loop = loop
        self.homeassistant = homeassistant
        self.websession = websession

    async def _api_client(self, request, path, timeout=300):
        """Return a client request with proxy origin for Home-Assistant."""
        url = f"{self.homeassistant.api_url}/api/{path}"

        try:
            data = None
            headers = {}
            method = getattr(self.websession, request.method.lower())

            # read data
            with async_timeout.timeout(30, loop=self.loop):
                data = await request.read()

            if data:
                headers.update({CONTENT_TYPE: request.content_type})

            # need api password?
            if self.homeassistant.api_password:
                headers = {HEADER_HA_ACCESS: self.homeassistant.api_password}

            # reset headers
            if not headers:
                headers = None

            client = await method(
                url, data=data, headers=headers, timeout=timeout
            )

            return client

        except aiohttp.ClientError as err:
            _LOGGER.error("Client error on API %s request %s.", path, err)

        except asyncio.TimeoutError:
            _LOGGER.error("Client timeout error on API request %s.", path)

        raise HTTPBadGateway()

    async def api(self, request):
        """Proxy HomeAssistant API Requests."""
        path = request.match_info.get('path', '')

        # API stream
        if path.startswith("stream"):
            _LOGGER.info("Home-Assistant Event-Stream start")
            client = await self._api_client(request, path, timeout=None)

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

            _LOGGER.info("Home-Assistant Event-Stream close")

        # Normal request
        else:
            _LOGGER.info("Home-Assistant '/api/%s' request", path)
            client = await self._api_client(request, path)

            data = await client.read()
            return web.Response(
                body=data,
                status=client.status,
                content_type=client.content_type
            )

    async def _websocket_client(self):
        """Initialize a websocket api connection."""
        url = f"{self.homeassistant.api_url}/api/websocket"

        try:
            client = await self.websession.ws_connect(
                url, heartbeat=60)

            # handle authentication
            for _ in range(2):
                data = await client.receive_json()
                if data.get('type') == 'auth_ok':
                    return client
                elif data.get('type') == 'auth_required':
                    await client.send_json({
                        'type': 'auth',
                        'api_password': self.homeassistant.api_password,
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
        await server.send_json({'type': 'auth_required'})
        await server.receive_json()  # get internal token
        await server.send_json({'type': 'auth_ok'})

        # init connection to hass
        client = await self._websocket_client()

        _LOGGER.info("Home-Assistant Websocket API request running")
        try:
            while not server.closed and not client.closed:
                client_read = asyncio.ensure_future(
                    client.receive_str(), loop=self.loop)
                server_read = asyncio.ensure_future(
                    client.receive_str(), loop=self.loop)

                # wait until data need to be processed
                await asyncio.wait(
                    [client_read, server_read],
                    loop=self.loop, return_when=asyncio.FIRST_COMPLETED
                )

                # server
                if server_read.done():
                    await client.send_str(server_read.result())
                # client
                if client_read.done():
                    await server.send_str(client_read.result())

                # error handling
                client_read.exception()
                server_read.exception()

        except (RuntimeError, asyncio.CancelledError):
            pass

        finally:
            await client.close()
            await server.close()

        _LOGGER.info("Home-Assistant Websocket API connection is closed")
