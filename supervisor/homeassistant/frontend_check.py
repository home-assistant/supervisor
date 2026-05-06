"""External frontend availability probes for Home Assistant Core.

These probes intentionally bypass the Supervisor-internal API layer
(authentication, Unix socket transport, retries) so they exercise the
same code paths an external HTTP/WebSocket client would. The goal is
to detect cases where Core's HTTP API responds but the user-facing
frontend or WebSocket endpoint is broken (e.g. due to a custom http
component override masking websocket_api).
"""

from __future__ import annotations

import asyncio
from contextlib import suppress
import logging

import aiohttp
from aiohttp import hdrs

from ..coresys import CoreSys

_LOGGER: logging.Logger = logging.getLogger(__name__)

_PROBE_TIMEOUT = aiohttp.ClientTimeout(total=30)
_WS_HANDSHAKE_TIMEOUT = 30.0
_WS_RECEIVE_TIMEOUT = 10.0


async def check_frontend(coresys: CoreSys) -> bool:
    """Verify the frontend serves HTML on the root path."""
    url = f"{coresys.homeassistant.api_url}/"
    try:
        async with coresys.websession.get(
            url, timeout=_PROBE_TIMEOUT, ssl=False
        ) as resp:
            if resp.status != 200:
                _LOGGER.error("Frontend returned status %s", resp.status)
                return False
            content_type = resp.headers.get(hdrs.CONTENT_TYPE, "")
            if "text/html" not in content_type:
                _LOGGER.error(
                    "Frontend responded with unexpected content type: %s",
                    content_type,
                )
                return False
    except (aiohttp.ClientError, TimeoutError) as err:
        _LOGGER.error("Cannot reach frontend at %s: %s", url, err)
        return False

    _LOGGER.debug("Frontend is accessible and serving HTML")
    return True


async def check_websocket(coresys: CoreSys) -> bool:
    """Verify the WebSocket endpoint accepts a handshake.

    We don't authenticate. A working endpoint sends an `auth_required`
    text frame immediately after the upgrade; that's enough to confirm
    websocket_api is wired up and functional.
    """
    url = coresys.homeassistant.ws_url
    ws: aiohttp.ClientWebSocketResponse | None = None
    try:
        ws = await asyncio.wait_for(
            coresys.websession.ws_connect(url, ssl=False),
            timeout=_WS_HANDSHAKE_TIMEOUT,
        )
        msg = await ws.receive(timeout=_WS_RECEIVE_TIMEOUT)
        if msg.type != aiohttp.WSMsgType.TEXT:
            _LOGGER.error("WebSocket handshake returned non-text message: %s", msg.type)
            return False
        data = msg.json()
        if not isinstance(data, dict) or data.get("type") != "auth_required":
            _LOGGER.error("WebSocket did not send auth_required, got: %s", data)
            return False
    except (aiohttp.ClientError, TimeoutError, ValueError) as err:
        _LOGGER.error("WebSocket probe to %s failed: %s", url, err)
        return False
    finally:
        if ws is not None:
            with suppress(Exception):
                await ws.close()

    _LOGGER.debug("WebSocket endpoint accepted handshake")
    return True


async def verify_frontend(coresys: CoreSys) -> bool:
    """Run both frontend probes; return True only if both succeed."""
    return await check_frontend(coresys) and await check_websocket(coresys)
