"""Test external frontend probes."""

from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from supervisor.coresys import CoreSys
from supervisor.homeassistant.frontend_check import (
    ProbeResult,
    check_api_reachable,
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
    """Frontend check returns OK for HTML 200."""
    websession.get = MagicMock(return_value=_mock_response(200, "text/html"))
    assert await check_frontend(coresys) is ProbeResult.OK


async def test_check_frontend_wrong_status(coresys: CoreSys, websession: MagicMock):
    """Frontend check returns BAD_RESPONSE on non-200 status."""
    websession.get = MagicMock(return_value=_mock_response(503, "text/html"))
    assert await check_frontend(coresys) is ProbeResult.BAD_RESPONSE


async def test_check_frontend_wrong_content_type(
    coresys: CoreSys, websession: MagicMock
):
    """Frontend check returns BAD_RESPONSE when content-type is not HTML."""
    websession.get = MagicMock(return_value=_mock_response(200, "application/json"))
    assert await check_frontend(coresys) is ProbeResult.BAD_RESPONSE


async def test_check_frontend_connection_error(coresys: CoreSys, websession: MagicMock):
    """Frontend check returns NO_RESPONSE on connection errors."""
    websession.get = MagicMock(side_effect=aiohttp.ClientConnectionError("boom"))
    assert await check_frontend(coresys) is ProbeResult.NO_RESPONSE


async def test_check_frontend_timeout(coresys: CoreSys, websession: MagicMock):
    """Frontend check returns BAD_RESPONSE on timeout (not a mutual-TLS reject)."""
    websession.get = MagicMock(side_effect=TimeoutError())
    assert await check_frontend(coresys) is ProbeResult.BAD_RESPONSE


# --- check_websocket ---


async def test_check_websocket_ok(coresys: CoreSys, websession: MagicMock):
    """Websocket check returns OK when auth_required is received."""
    msg = MagicMock()
    msg.type = aiohttp.WSMsgType.TEXT
    msg.json.return_value = {"type": "auth_required"}
    websession.ws_connect = AsyncMock(return_value=_mock_ws(msg))
    assert await check_websocket(coresys) is ProbeResult.OK


async def test_check_websocket_close_frame(coresys: CoreSys, websession: MagicMock):
    """Websocket check returns BAD_RESPONSE on close frame (issue #6802 case)."""
    msg = MagicMock()
    msg.type = aiohttp.WSMsgType.CLOSE
    websession.ws_connect = AsyncMock(return_value=_mock_ws(msg))
    assert await check_websocket(coresys) is ProbeResult.BAD_RESPONSE


async def test_check_websocket_unexpected_message(
    coresys: CoreSys, websession: MagicMock
):
    """Websocket check returns BAD_RESPONSE when first frame is not auth_required."""
    msg = MagicMock()
    msg.type = aiohttp.WSMsgType.TEXT
    msg.json.return_value = {"type": "result"}
    websession.ws_connect = AsyncMock(return_value=_mock_ws(msg))
    assert await check_websocket(coresys) is ProbeResult.BAD_RESPONSE


async def test_check_websocket_connect_error(coresys: CoreSys, websession: MagicMock):
    """Websocket check returns NO_RESPONSE if the handshake fails."""
    websession.ws_connect = AsyncMock(side_effect=aiohttp.ClientConnectionError("nope"))
    assert await check_websocket(coresys) is ProbeResult.NO_RESPONSE


async def test_check_websocket_handshake_timeout(
    coresys: CoreSys, websession: MagicMock
):
    """Websocket check returns BAD_RESPONSE on handshake timeout, not NO_RESPONSE."""
    websession.ws_connect = AsyncMock(side_effect=TimeoutError())
    assert await check_websocket(coresys) is ProbeResult.BAD_RESPONSE


async def test_check_websocket_non_dict_payload(
    coresys: CoreSys, websession: MagicMock
):
    """Websocket check returns BAD_RESPONSE when payload is JSON but not an object."""
    msg = MagicMock()
    msg.type = aiohttp.WSMsgType.TEXT
    msg.json.return_value = ["auth_required"]
    websession.ws_connect = AsyncMock(return_value=_mock_ws(msg))
    assert await check_websocket(coresys) is ProbeResult.BAD_RESPONSE


# --- check_api_reachable ---


async def test_check_api_reachable_ok(coresys: CoreSys):
    """API reachability check returns True when a TCP connection succeeds."""
    writer = MagicMock()
    writer.wait_closed = AsyncMock()
    with patch(
        "supervisor.homeassistant.frontend_check.asyncio.open_connection",
        AsyncMock(return_value=(MagicMock(), writer)),
    ):
        assert await check_api_reachable(coresys) is True
    writer.close.assert_called_once()


async def test_check_api_reachable_connection_error(coresys: CoreSys):
    """API reachability check returns False when the connection fails."""
    with patch(
        "supervisor.homeassistant.frontend_check.asyncio.open_connection",
        AsyncMock(side_effect=ConnectionResetError("boom")),
    ):
        assert await check_api_reachable(coresys) is False


# --- verify_frontend ---


@pytest.mark.parametrize(
    ("frontend", "websocket", "expected"),
    [
        (ProbeResult.OK, ProbeResult.OK, True),
        (ProbeResult.BAD_RESPONSE, ProbeResult.OK, False),
        (ProbeResult.OK, ProbeResult.BAD_RESPONSE, False),
        # No response without SSL is a plain connectivity failure.
        (ProbeResult.NO_RESPONSE, ProbeResult.NO_RESPONSE, False),
    ],
)
async def test_verify_frontend(
    coresys: CoreSys,
    frontend: ProbeResult,
    websocket: ProbeResult,
    expected: bool,
):
    """verify_frontend combines both probe results without SSL."""
    with (
        patch(
            "supervisor.homeassistant.frontend_check.check_frontend",
            AsyncMock(return_value=frontend),
        ),
        patch(
            "supervisor.homeassistant.frontend_check.check_websocket",
            AsyncMock(return_value=websocket),
        ),
    ):
        assert await verify_frontend(coresys) is expected


async def test_verify_frontend_ssl_bad_response_fails(coresys: CoreSys):
    """A bad response under SSL is a genuine failure, not a mutual-TLS reject."""
    coresys.homeassistant.api_ssl = True
    with (
        patch(
            "supervisor.homeassistant.frontend_check.check_frontend",
            AsyncMock(return_value=ProbeResult.BAD_RESPONSE),
        ),
        patch(
            "supervisor.homeassistant.frontend_check.check_websocket",
            AsyncMock(return_value=ProbeResult.NO_RESPONSE),
        ),
        patch(
            "supervisor.homeassistant.frontend_check.check_api_reachable",
            AsyncMock(return_value=True),
        ) as reachable,
    ):
        assert await verify_frontend(coresys) is False
    reachable.assert_not_called()


@pytest.mark.parametrize("reachable", [True, False])
async def test_verify_frontend_ssl_no_response_uses_tcp_check(
    coresys: CoreSys, reachable: bool
):
    """Probes that get no response under SSL fall back to the TCP check (#6987)."""
    coresys.homeassistant.api_ssl = True
    with (
        patch(
            "supervisor.homeassistant.frontend_check.check_frontend",
            AsyncMock(return_value=ProbeResult.NO_RESPONSE),
        ),
        patch(
            "supervisor.homeassistant.frontend_check.check_websocket",
            AsyncMock(return_value=ProbeResult.NO_RESPONSE),
        ),
        patch(
            "supervisor.homeassistant.frontend_check.check_api_reachable",
            AsyncMock(return_value=reachable),
        ) as check,
    ):
        assert await verify_frontend(coresys) is reachable
    check.assert_awaited_once_with(coresys)
