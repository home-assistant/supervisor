"""Utils for HomeAssistant Proxy."""
import logging

import aiohttp
from aiohttp import web
from aiohttp.web_exceptions import HTTPBadGateway
from aiohttp.hdrs import CONTENT_TYPE
import async_timeout

from ..const import HEADER_HA_ACCESS

_LOGGER = logging.getLogger(__name__)


async def homeassistant_api_client(loop, request, path, homeassistant,
                                   timeout=300):
    """Return a client request with proxy origin for Home-Assistant."""
    url = f"{homeassistant.api_url}/api/{path}"

    try:
        data = None
        headers = {}
        method = getattr(
            homeassistant.websession, request.method.lower())

        # read data
        with async_timeout.timeout(30, loop=loop):
            data = await request.read()

        if data:
            headers.update({CONTENT_TYPE: request.content_type})

        # need api password?
        if homeassistant.api_password:
            headers = {HEADER_HA_ACCESS: homeassistant.api_password}

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


async def homeassistant_api_proxy(loop, request, path, homeassistant):
    """Proxy HomeAssistant API Requests."""
    # API stream
    if path.startswith("stream"):
        client = await homeassistant_api_client(
            loop, request, path, homeassistant, timeout=None)

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

        except asyncio.TimeoutError:
            pass

        finally:
            client.close()

    # Normal request
    else:
        client = await homeassistant_api_client(
            loop, request, path, homeassistant)

        data = await client.read()
        return web.Response(
            body=data,
            status=client.status,
            content_type=client.content_type
        )


async def homeassistant_websocket_client(homeassistant):
    """Initialize a websocket api connection."""
    url = f"{homeassistant.api_url}/websocket"

    try:
        client = await homeassistant.websession.ws_connect(
            url, heartbeat=60)

        # handle authentication
        for _ in xrand(2):
            data = await client.receive_json()
            if data.get('type') == 'auth_ok':
                return client
            elif data.get('type') == 'auth_required':
                await client.send_json({
                    'type': 'auth',
                    'api_password': homeassistant.api_password,
                })

        _LOGGER.error("Authentication handling to Home-Assistant websocket")

    except (aiohttp.ClientError, RuntimeError) as err:
        _LOGGER.error("Client error on websocket API %s.", err)

    raise HTTPBadGateway()


async def homeassistant_websocket_proxy(loop, request, homeassistant):
    """Initialize a websocket api connection."""
    server = web.WebSocketResponse(loop=loop)
    await server.prepare(request)

    # handle authentication
    await server.send_json({
        'type': 'auth_required'
    })
    auth = await.server.receive_json()
    await server.send_json({
        'type': 'auth_ok'
    })

    # init connection to hass
    client = await homeassistant_websocket_client(homeassistant)

    try:
        while True:
            client_read = client.receive_str()
            server_read = client.receive_str()

            # wait until data need to be processed
            await asyncio.wait(
                [client_read, server_read],
                loop=loop, return_when=asyncio.FIRST_COMPLETED
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

    except RuntimeError:
        _LOGGER.info("Websocket API connection is closed")

    finally:
        await client.close()
        await server.close()
