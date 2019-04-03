"""Hass.io Add-on ingress service."""
import asyncio
from ipaddress import ip_address
import logging
from typing import Dict, Union

import aiohttp
from aiohttp import hdrs, web
from aiohttp.web_exceptions import (
    HTTPBadGateway,
    HTTPServiceUnavailable,
    HTTPUnauthorized,
)
from multidict import CIMultiDict, istr

from ..addons.addon import Addon
from ..const import HEADER_TOKEN, REQUEST_FROM
from ..coresys import CoreSysAttributes

_LOGGER = logging.getLogger(__name__)


class APIIngress(CoreSysAttributes):
    """Ingress view to handle add-on webui routing."""

    def _extract_addon(self, request: web.Request) -> Addon:
        """Return addon, throw an exception it it doesn't exist."""
        addon_slug = request.match_info.get("addon")

        try:
            addon = self.sys_addons.get(addon_slug)
            assert addon
            assert not addon.is_installed

        except AssertionError:
            _LOGGER.warning("Ingress for %s not available", addon_slug)
            raise HTTPServiceUnavailable() from None

        return addon

    def _create_url(self, addon: Addon, path: str) -> str:
        """Create URL to container."""
        return f"{addon.ingress_url}/{path}"

    async def handler(
        self, request: web.Request
    ) -> Union[web.Response, web.StreamResponse, web.WebSocketResponse]:
        """Route data to Hass.io ingress service."""
        addon = self._extract_addon(request)
        path = request.match_info.get("path")

        # Only Home Assistant call this
        if request[REQUEST_FROM] != self.sys_homeassistant:
            _LOGGER.warning("Ingress is only available behind Home Assistant")
            raise HTTPUnauthorized()
        if not addon.with_ingress:
            _LOGGER.warning("Add-on %s don't support ingress feature", addon.slug)
            raise HTTPBadGateway() from None

        # Process requests
        try:
            # Websocket
            if _is_websocket(request):
                return await self._handle_websocket(request, addon, path)

            # Request
            return await self._handle_request(request, addon, path)

        except aiohttp.ClientError:
            pass

        raise HTTPBadGateway() from None

    async def _handle_websocket(
        self, request: web.Request, addon: Addon, path: str
    ) -> web.WebSocketResponse:
        """Ingress route for websocket."""
        ws_server = web.WebSocketResponse()
        await ws_server.prepare(request)

        # Preparing
        url = self._create_url(addon, path)
        source_header = _init_header(request, addon)

        # Support GET query
        if request.query_string:
            url = "{}?{}".format(url, request.query_string)

        # Start proxy
        async with self.sys_websession.ws_connect(
            url, headers=source_header
        ) as ws_client:
            # Proxy requests
            await asyncio.wait(
                [
                    _websocket_forward(ws_server, ws_client),
                    _websocket_forward(ws_client, ws_server),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )

        return ws_server

    async def _handle_request(
        self, request: web.Request, addon: Addon, path: str
    ) -> Union[web.Response, web.StreamResponse]:
        """Ingress route for request."""
        url = self._create_url(addon, path)
        data = await request.read()
        source_header = _init_header(request, addon)

        async with self.sys_websession.request(
            request.method,
            url,
            headers=source_header,
            params=request.query,
            data=data,
            cookies=request.cookies,
        ) as result:
            headers = _response_header(result)

            # Simple request
            if (
                hdrs.CONTENT_LENGTH in result.headers
                and int(result.headers.get(hdrs.CONTENT_LENGTH, 0)) < 4_194_000
            ):
                # Return Response
                body = await result.read()
                return web.Response(headers=headers, status=result.status, body=body)

            # Stream response
            response = web.StreamResponse(status=result.status, headers=headers)
            response.content_type = result.content_type

            try:
                await response.prepare(request)
                async for data in result.content:
                    await response.write(data)

            except (aiohttp.ClientError, aiohttp.ClientPayloadError):
                pass

            return response


def _init_header(
    request: web.Request, addon: str
) -> Union[CIMultiDict, Dict[str, str]]:
    """Create initial header."""
    headers = {}

    # filter flags
    for name, value in request.headers.items():
        if name in (hdrs.CONTENT_LENGTH, hdrs.CONTENT_TYPE, istr(HEADER_TOKEN)):
            continue
        headers[name] = value

    # Update X-Forwarded-For
    forward_for = request.headers.get(hdrs.X_FORWARDED_FOR)
    connected_ip = ip_address(request.transport.get_extra_info("peername")[0])
    headers[hdrs.X_FORWARDED_FOR] = f"{forward_for}, {connected_ip!s}"

    return headers


def _response_header(response: aiohttp.ClientResponse) -> Dict[str, str]:
    """Create response header."""
    headers = {}

    for name, value in response.headers.items():
        if name in (hdrs.TRANSFER_ENCODING, hdrs.CONTENT_LENGTH, hdrs.CONTENT_TYPE):
            continue
        headers[name] = value

    return headers


def _is_websocket(request: web.Request) -> bool:
    """Return True if request is a websocket."""
    headers = request.headers

    if (
        headers.get(hdrs.CONNECTION) == "Upgrade"
        and headers.get(hdrs.UPGRADE) == "websocket"
    ):
        return True
    return False


async def _websocket_forward(ws_from, ws_to):
    """Handle websocket message directly."""
    async for msg in ws_from:
        if msg.type == aiohttp.WSMsgType.TEXT:
            await ws_to.send_str(msg.data)
        elif msg.type == aiohttp.WSMsgType.BINARY:
            await ws_to.send_bytes(msg.data)
        elif msg.type == aiohttp.WSMsgType.PING:
            await ws_to.ping()
        elif msg.type == aiohttp.WSMsgType.PONG:
            await ws_to.pong()
        elif ws_to.closed:
            await ws_to.close(code=ws_to.close_code, message=msg.extra)
