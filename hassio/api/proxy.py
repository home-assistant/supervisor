"""Utils for HomeAssistant Proxy."""
import asyncio
from contextlib import asynccontextmanager
import logging

import aiohttp
from aiohttp import web
from aiohttp.web_exceptions import (
    HTTPBadGateway, HTTPInternalServerError, HTTPUnauthorized)
from aiohttp.hdrs import CONTENT_TYPE
import async_timeout

from ..const import HEADER_HA_ACCESS
from ..coresys import CoreSysAttributes
from ..exceptions import HomeAssistantAuthError, HomeAssistantAPIError

_LOGGER = logging.getLogger(__name__)


class APIProxy(CoreSysAttributes):
    """API Proxy for Home-Assistant."""

    def _check_access(self, request):
        """Check the Hass.io token."""
        hassio_token = request.headers.get(HEADER_HA_ACCESS)
        addon = self.sys_addons.from_uuid(hassio_token)

        if not addon:
            _LOGGER.warning("Unknown HomeAssistant API access!")
        elif not addon.access_homeassistant_api:
            _LOGGER.warning("Not permitted API access: %s", addon.slug)
        else:
            _LOGGER.info("%s access from %s", request.path, addon.slug)
            return

        raise HTTPUnauthorized()

    @asynccontextmanager
    async def _api_client(self, request, path, timeout=300):
        """Return a client request with proxy origin for Home-Assistant."""
        try:
            # read data
            with async_timeout.timeout(30):
                data = await request.read()

            if data:
                content_type = request.content_type
            else:
                content_type = None

            async with self.sys_homeassistant.make_request(
                    request.method.lower(), f'api/{path}',
                    content_type=content_type,
                    data=data,
                    timeout=timeout,
            ) as resp:
                yield resp
                return

        except HomeAssistantAPIError:
            _LOGGER.error("Authenticate error on API for request %s", path)
        except aiohttp.ClientError as err:
            _LOGGER.error("Client error on API %s request %s", path, err)
        except asyncio.TimeoutError:
            _LOGGER.error("Client timeout error on API request %s", path)

        raise HTTPBadGateway()

    async def stream(self, request):
        """Proxy HomeAssistant EventStream Requests."""
        self._check_access(request)

        _LOGGER.info("Home-Assistant EventStream start")
        async with self._api_client(request, 'stream', timeout=None) as client:
            response = web.StreamResponse()
            response.content_type = request.headers.get(CONTENT_TYPE)
            try:
                await response.prepare(request)
                while True:
                    data = await client.content.read(10)
                    if not data:
                        break
                    await response.write(data)

            except aiohttp.ClientError:
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
        async with self._api_client(request, path) as client:
            data = await client.read()
            return web.Response(
                body=data,
                status=client.status,
                content_type=client.content_type
            )

    async def _websocket_client(self):
        """Initialize a websocket api connection."""
        url = f"{self.sys_homeassistant.api_url}/api/websocket"

        try:
            client = await self.sys_websession_ssl.ws_connect(
                url, heartbeat=60, verify_ssl=False)

            # handle authentication
            data = await client.receive_json()

            if data.get('type') == 'auth_ok':
                return client

            if data.get('type') != 'auth_required':
                # Invalid protocol
                _LOGGER.error(
                    'Got unexpected response from HA websocket: %s', data)
                raise HTTPBadGateway()

            if self.sys_homeassistant.refresh_token:
                await self.sys_homeassistant.ensure_access_token()
                await client.send_json({
                    'type': 'auth',
                    'access_token': self.sys_homeassistant.access_token,
                })
            else:
                await client.send_json({
                    'type': 'auth',
                    'api_password': self.sys_homeassistant.api_password,
                })

            data = await client.receive_json()

            if data.get('type') == 'auth_ok':
                return client

            # Renew the Token is invalid
            if (data.get('type') == 'invalid_auth' and
                    self.sys_homeassistant.refresh_token):
                self.sys_homeassistant.access_token = None
                return await self._websocket_client()

            _LOGGER.error(
                "Failed authentication to Home-Assistant websocket: %s", data)

        except (RuntimeError, HomeAssistantAuthError, ValueError) as err:
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
                'ha_version': self.sys_homeassistant.version,
            })

            # Check API access
            response = await server.receive_json()
            hassio_token = (response.get('api_password') or
                            response.get('access_token'))
            addon = self.sys_addons.from_uuid(hassio_token)

            if not addon or not addon.access_homeassistant_api:
                _LOGGER.warning("Unauthorized websocket access!")
                await server.send_json({
                    'type': 'auth_invalid',
                    'message': 'Invalid access',
                })
                return server

            _LOGGER.info("Websocket access from %s", addon.slug)

            await server.send_json({
                'type': 'auth_ok',
                'ha_version': self.sys_homeassistant.version,
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
                    client_read = self.sys_create_task(
                        client.receive_str())
                if not server_read:
                    server_read = self.sys_create_task(
                        server.receive_str())

                # wait until data need to be processed
                await asyncio.wait(
                    [client_read, server_read],
                    return_when=asyncio.FIRST_COMPLETED
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
