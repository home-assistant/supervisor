"""Test API utils."""

import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock, patch
import weakref

from aiohttp import ClientConnectionResetError, WSCloseCode, web
import pytest

from supervisor.api.const import WEBSOCKETS
from supervisor.api.utils import prepare_websocket, stop_on_disconnect
from supervisor.const import CoreState


@pytest.fixture(autouse=True)
def fast_disconnect_check():
    """Check for client disconnects without delay."""
    with patch("supervisor.api.utils.DISCONNECT_CHECK_INTERVAL", 0):
        yield


async def test_stop_on_disconnect_stops_block():
    """Test the wrapped block is stopped once the client disconnects."""
    request = MagicMock()
    request.transport.is_closing.return_value = False
    reached_end = False

    async def handler() -> str:
        nonlocal reached_end
        async with stop_on_disconnect(request):
            await asyncio.sleep(3600)
            reached_end = True
        return "done"

    task = asyncio.create_task(handler())
    await asyncio.sleep(0.01)
    assert not task.done()

    request.transport = None
    assert await asyncio.wait_for(task, 1) == "done"
    assert not reached_end
    assert task.cancelling() == 0


async def test_stop_on_disconnect_connected():
    """Test the wrapped block runs normally while the client is connected."""
    request = MagicMock()
    request.transport.is_closing.return_value = False

    async with stop_on_disconnect(request):
        await asyncio.sleep(0.01)

    assert asyncio.current_task().cancelling() == 0


async def test_stop_on_disconnect_external_cancel():
    """Test cancellation not caused by a disconnect is propagated."""
    request = MagicMock()
    request.transport.is_closing.return_value = False

    async def handler() -> None:
        async with stop_on_disconnect(request):
            await asyncio.sleep(3600)

    task = asyncio.create_task(handler())
    await asyncio.sleep(0.01)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


async def test_prepare_websocket_success():
    """Test prepare_websocket prepares and registers a WebSocket."""
    request = MagicMock(spec=web.Request)
    request.transport.is_closing.return_value = False
    websockets: weakref.WeakSet[web.WebSocketResponse] = weakref.WeakSet()
    request.config_dict = {WEBSOCKETS: websockets}

    ws_response = MagicMock(spec=web.WebSocketResponse)
    ws_response.prepare = AsyncMock()
    ws_response.close = AsyncMock()

    coresys = MagicMock()
    coresys.core.state = CoreState.RUNNING

    result = await prepare_websocket(request, ws_response, coresys)

    assert result is True
    ws_response.prepare.assert_awaited_once_with(request)
    ws_response.close.assert_not_awaited()
    assert ws_response in websockets


async def test_prepare_websocket_stopping():
    """Test prepare_websocket closes the socket when Supervisor stops."""
    request = MagicMock(spec=web.Request)
    request.transport.is_closing.return_value = False
    websockets: weakref.WeakSet[web.WebSocketResponse] = weakref.WeakSet()
    request.config_dict = {WEBSOCKETS: websockets}

    ws_response = MagicMock(spec=web.WebSocketResponse)
    ws_response.prepare = AsyncMock()
    ws_response.close = AsyncMock()

    coresys = MagicMock()
    coresys.core.state = CoreState.STOPPING

    result = await prepare_websocket(request, ws_response, coresys)

    assert result is False
    assert ws_response in websockets
    ws_response.close.assert_awaited_once_with(code=WSCloseCode.GOING_AWAY)


async def test_prepare_websocket_transport_none(caplog: pytest.LogCaptureFixture):
    """Test prepare_websocket raises HTTPBadRequest when transport is None."""
    request = MagicMock(spec=web.Request)
    request.transport = None
    ws_response = MagicMock(spec=web.WebSocketResponse)
    ws_response.prepare = AsyncMock()
    coresys = MagicMock()

    caplog.clear()
    with (
        caplog.at_level(logging.WARNING),
        pytest.raises(web.HTTPBadRequest) as exc_info,
    ):
        await prepare_websocket(
            request,
            ws_response,
            coresys,
            disconnect_log_level=logging.WARNING,
        )

    assert exc_info.value.reason == "Connection closed"
    ws_response.prepare.assert_not_awaited()
    assert "WebSocket connection lost before upgrade" in caplog.text


async def test_prepare_websocket_transport_closing(caplog: pytest.LogCaptureFixture):
    """Test prepare_websocket raises HTTPBadRequest when transport is closing."""
    request = MagicMock(spec=web.Request)
    request.transport.is_closing.return_value = True
    ws_response = MagicMock(spec=web.WebSocketResponse)
    ws_response.prepare = AsyncMock()
    coresys = MagicMock()

    caplog.clear()
    with (
        caplog.at_level(logging.DEBUG),
        pytest.raises(web.HTTPBadRequest) as exc_info,
    ):
        await prepare_websocket(request, ws_response, coresys)

    assert exc_info.value.reason == "Connection closed"
    ws_response.prepare.assert_not_awaited()
    assert "WebSocket connection lost before upgrade" in caplog.text


@pytest.mark.parametrize(
    "error",
    [
        ClientConnectionResetError("Cannot write to closing transport"),
        ConnectionError("Connection lost"),
    ],
)
async def test_prepare_websocket_pre_upgrade_connection_error(
    error: ConnectionError,
    caplog: pytest.LogCaptureFixture,
):
    """Test prepare_websocket raises HTTPBadRequest on pre-upgrade disconnect."""
    request = MagicMock(spec=web.Request)
    request.transport.is_closing.return_value = False
    ws_response = MagicMock(spec=web.WebSocketResponse)
    ws_response.prepared = False
    ws_response.prepare = AsyncMock(side_effect=error)
    ws_response.close = AsyncMock()
    coresys = MagicMock()

    caplog.clear()
    with (
        caplog.at_level(logging.DEBUG),
        pytest.raises(web.HTTPBadRequest) as exc_info,
    ):
        await prepare_websocket(request, ws_response, coresys)

    assert exc_info.value.reason == "Connection closed"
    ws_response.close.assert_not_awaited()
    assert "WebSocket connection lost before upgrade" in caplog.text


async def test_prepare_websocket_post_prepare_drain_connection_error(
    caplog: pytest.LogCaptureFixture,
):
    """Test prepare_websocket closes the socket if drain fails after prepare."""
    request = MagicMock(spec=web.Request)
    request.transport.is_closing.return_value = False
    websockets: weakref.WeakSet[web.WebSocketResponse] = weakref.WeakSet()
    request.config_dict = {WEBSOCKETS: websockets}

    ws_response = MagicMock(spec=web.WebSocketResponse)
    ws_response.prepared = False
    ws_response.close = AsyncMock()

    async def fail_after_prepare(_req: web.Request) -> None:
        ws_response.prepared = True
        raise ConnectionError("Connection lost")

    ws_response.prepare = AsyncMock(side_effect=fail_after_prepare)
    coresys = MagicMock()
    coresys.core.state = CoreState.RUNNING

    caplog.clear()
    with caplog.at_level(logging.DEBUG):
        result = await prepare_websocket(request, ws_response, coresys)

    assert result is False
    ws_response.close.assert_awaited_once()
    assert ws_response not in websockets
    assert "WebSocket connection lost during upgrade" in caplog.text
