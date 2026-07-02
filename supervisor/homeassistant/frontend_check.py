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
from enum import Enum
import logging

import aiohttp
from aiohttp import hdrs

from ..coresys import CoreSys

_LOGGER: logging.Logger = logging.getLogger(__name__)

_PROBE_TIMEOUT = aiohttp.ClientTimeout(total=30)
_WS_HANDSHAKE_TIMEOUT = 30.0
_WS_RECEIVE_TIMEOUT = 10.0


class ProbeResult(Enum):
    """Outcome of an external frontend probe.

    The distinction between BAD_RESPONSE and NO_RESPONSE matters: both mean
    the frontend is genuinely broken and warrant a rollback, except that
    NO_RESPONSE is specifically a connection that was reset or dropped before
    we got anything. That is exactly how Core rejects us when it requires a
    client certificate (`ssl_peer_certificate`) that we don't present, so
    NO_RESPONSE must not by itself be treated as a broken frontend.

    A timeout is deliberately BAD_RESPONSE, not NO_RESPONSE: mutual TLS
    rejects an unauthenticated connection within a few packets, so it never
    manifests as a timeout. A probe that times out reached the listener but
    never answered, which points to a real problem rather than mutual TLS.
    """

    OK = "ok"
    BAD_RESPONSE = "bad_response"
    NO_RESPONSE = "no_response"


async def check_frontend(coresys: CoreSys) -> ProbeResult:
    """Verify the frontend serves HTML on the root path."""
    url = f"{coresys.homeassistant.api_url}/"
    try:
        async with coresys.websession.get(
            url, timeout=_PROBE_TIMEOUT, ssl=False
        ) as resp:
            if resp.status != 200:
                _LOGGER.error("Frontend returned status %s", resp.status)
                return ProbeResult.BAD_RESPONSE
            content_type = resp.headers.get(hdrs.CONTENT_TYPE, "")
            if "text/html" not in content_type:
                _LOGGER.error(
                    "Frontend responded with unexpected content type: %s",
                    content_type,
                )
                return ProbeResult.BAD_RESPONSE
    except TimeoutError:
        _LOGGER.error("Frontend at %s did not respond in time", url)
        return ProbeResult.BAD_RESPONSE
    except aiohttp.ClientError as err:
        _LOGGER.error("Cannot reach frontend at %s: %s", url, err)
        return ProbeResult.NO_RESPONSE

    _LOGGER.debug("Frontend is accessible and serving HTML")
    return ProbeResult.OK


async def check_websocket(coresys: CoreSys) -> ProbeResult:
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
    except TimeoutError:
        _LOGGER.error("WebSocket handshake with %s did not complete in time", url)
        return ProbeResult.BAD_RESPONSE
    except aiohttp.ClientError as err:
        _LOGGER.error("WebSocket probe to %s failed: %s", url, err)
        return ProbeResult.NO_RESPONSE

    try:
        msg = await ws.receive(timeout=_WS_RECEIVE_TIMEOUT)
        if msg.type != aiohttp.WSMsgType.TEXT:
            _LOGGER.error("WebSocket handshake returned non-text message: %s", msg.type)
            return ProbeResult.BAD_RESPONSE
        data = msg.json()
        if not isinstance(data, dict) or data.get("type") != "auth_required":
            _LOGGER.error("WebSocket did not send auth_required, got: %s", data)
            return ProbeResult.BAD_RESPONSE
    except (TimeoutError, ValueError) as err:
        # The handshake already succeeded; failing to read or parse the first
        # frame means the endpoint connected but is misbehaving.
        _LOGGER.error("WebSocket handshake on %s returned no valid frame: %s", url, err)
        return ProbeResult.BAD_RESPONSE
    finally:
        with suppress(Exception):
            await ws.close()

    _LOGGER.debug("WebSocket endpoint accepted handshake")
    return ProbeResult.OK


async def check_api_reachable(coresys: CoreSys) -> bool:
    """Verify Core is accepting connections on its API port.

    This only establishes a TCP connection; it does not attempt a TLS
    handshake or send any data. It's used as a fallback when the HTTP and
    WebSocket probes can't connect at all, which is expected for a mutual-TLS
    setup (`ssl_peer_certificate`): Core resets the handshake because we don't
    present a client certificate. Reaching the listener is the most we can
    confirm in that case.
    """
    host = str(coresys.homeassistant.ip_address)
    port = coresys.homeassistant.api_port
    writer: asyncio.StreamWriter | None = None
    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=_PROBE_TIMEOUT.total
        )
    except (OSError, TimeoutError) as err:
        _LOGGER.error("Cannot reach Core API at %s:%s: %s", host, port, err)
        return False
    finally:
        if writer is not None:
            writer.close()
            with suppress(OSError):
                await writer.wait_closed()

    _LOGGER.debug("Core API port is reachable")
    return True


async def verify_frontend(coresys: CoreSys) -> bool:
    """Verify the frontend is available after an update.

    A probe that connects but returns a bad response means the frontend is
    genuinely broken, so we fail regardless of SSL. If the probes can't
    connect at all while Core is configured with SSL, we can't rule out a
    mutual-TLS setup (`ssl_peer_certificate`) rejecting our unauthenticated
    connection, so we fall back to a plain TCP reachability check instead of
    forcing a rollback, relying on the component check done by the caller.
    """
    frontend = await check_frontend(coresys)
    websocket = await check_websocket(coresys)

    if frontend == ProbeResult.OK and websocket == ProbeResult.OK:
        return True

    if ProbeResult.BAD_RESPONSE in (frontend, websocket):
        return False

    # Neither probe got a response. Outside of SSL that's a plain
    # connectivity failure; under SSL it's most likely mutual TLS rejecting
    # us, so confirm the listener is up rather than rolling back blindly.
    if coresys.homeassistant.api_ssl:
        _LOGGER.debug(
            "Frontend probes could not connect while Core uses SSL, "
            "falling back to API port reachability check"
        )
        return await check_api_reachable(coresys)

    return False
