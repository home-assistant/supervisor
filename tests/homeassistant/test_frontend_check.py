"""Test external frontend probes."""

from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest

from supervisor.coresys import CoreSys
from supervisor.homeassistant.frontend_check import (
    check_frontend,
    check_websocket,
    verify_frontend,
)


@asynccontextmanager
async def _mock_response(status: int, content_type: str):
    resp = MagicMock()
    resp.status = status
    resp.headers = {"Content-Type": content_type}
    yield resp


def _mock_ws(receive_msg) -> AsyncMock:
    ws = AsyncMock()
    ws.receive = AsyncMock(return_value=receive_msg)
    ws.close = AsyncMock()
    return ws


# --- check_frontend ---


async def test_check_frontend_ok(coresys: CoreSys, websession: MagicMock):
    """Frontend check returns True for HTML 200."""
    websession.get = MagicMock(return_value=_mock_response(200, "text/html"))
    assert await check_frontend(coresys) is True


async def test_check_frontend_wrong_status(coresys: CoreSys, websession: MagicMock):
    """Frontend check returns False on non-200 status."""
    websession.get = MagicMock(return_value=_mock_response(503, "text/html"))
    assert await check_frontend(coresys) is False


async def test_check_frontend_wrong_content_type(
    coresys: CoreSys, websession: MagicMock
):
    """Frontend check returns False when content-type is not HTML."""
    websession.get = MagicMock(return_value=_mock_response(200, "application/json"))
    assert await check_frontend(coresys) is False


async def test_check_frontend_connection_error(coresys: CoreSys, websession: MagicMock):
    """Frontend check returns False on connection errors."""
    websession.get = MagicMock(side_effect=aiohttp.ClientConnectionError("boom"))
    assert await check_frontend(coresys) is False


# --- check_websocket ---


async def test_check_websocket_ok(coresys: CoreSys, websession: MagicMock):
    """Websocket check returns True when auth_required is received."""
    msg = MagicMock()
    msg.type = aiohttp.WSMsgType.TEXT
    msg.json.return_value = {"type": "auth_required"}
    websession.ws_connect = AsyncMock(return_value=_mock_ws(msg))
    assert await check_websocket(coresys) is True


async def test_check_websocket_close_frame(coresys: CoreSys, websession: MagicMock):
    """Websocket check returns False on close frame (issue #6802 case)."""
    msg = MagicMock()
    msg.type = aiohttp.WSMsgType.CLOSE
    websession.ws_connect = AsyncMock(return_value=_mock_ws(msg))
    assert await check_websocket(coresys) is False


async def test_check_websocket_unexpected_message(
    coresys: CoreSys, websession: MagicMock
):
    """Websocket check returns False when first frame is not auth_required."""
    msg = MagicMock()
    msg.type = aiohttp.WSMsgType.TEXT
    msg.json.return_value = {"type": "result"}
    websession.ws_connect = AsyncMock(return_value=_mock_ws(msg))
    assert await check_websocket(coresys) is False


async def test_check_websocket_connect_error(coresys: CoreSys, websession: MagicMock):
    """Websocket check returns False if the handshake fails."""
    websession.ws_connect = AsyncMock(side_effect=aiohttp.ClientConnectionError("nope"))
    assert await check_websocket(coresys) is False


# --- verify_frontend ---


@pytest.mark.parametrize(
    ("frontend_ok", "ws_ok", "expected"),
    [(True, True, True), (False, True, False), (True, False, False)],
)
async def test_verify_frontend(
    coresys: CoreSys,
    websession: MagicMock,
    frontend_ok: bool,
    ws_ok: bool,
    expected: bool,
):
    """verify_frontend is True only if both probes succeed."""
    websession.get = MagicMock(
        return_value=_mock_response(200 if frontend_ok else 500, "text/html")
    )
    msg = MagicMock()
    msg.type = aiohttp.WSMsgType.TEXT
    msg.json.return_value = {"type": "auth_required" if ws_ok else "result"}
    websession.ws_connect = AsyncMock(return_value=_mock_ws(msg))

    assert await verify_frontend(coresys) is expected
