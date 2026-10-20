"""Test websocket."""

# pylint: disable=import-error
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.exceptions import HomeAssistantAPIError, HomeAssistantWSConnectionError
from supervisor.homeassistant.const import WSEvent, WSType
from supervisor.homeassistant.websocket import WSClient


async def test_send_command(coresys: CoreSys, ha_ws_client: AsyncMock):
    """Test sending a command returns a response."""
    await coresys.homeassistant.websocket.async_send_command({"type": "test"})
    ha_ws_client.async_send_command.assert_called_with({"type": "test"})

    await coresys.homeassistant.websocket.async_supervisor_update_event(
        "test", {"lorem": "ipsum"}
    )
    ha_ws_client.async_send_command.assert_called_with(
        {
            "type": WSType.SUPERVISOR_EVENT,
            "data": {
                "event": WSEvent.SUPERVISOR_UPDATE,
                "update_key": "test",
                "data": {"lorem": "ipsum"},
            },
        }
    )


async def test_fire_and_forget_during_startup(
    coresys: CoreSys, ha_ws_client: AsyncMock
):
    """Test fire-and-forget commands queue during startup and replay when running."""
    await coresys.homeassistant.websocket.load()
    await coresys.core.set_state(CoreState.SETUP)

    await coresys.homeassistant.websocket.async_supervisor_update_event(
        "test", {"lorem": "ipsum"}
    )
    ha_ws_client.async_send_command.assert_not_called()

    await coresys.core.set_state(CoreState.RUNNING)
    await asyncio.sleep(0)

    assert ha_ws_client.async_send_command.call_count == 2
    assert ha_ws_client.async_send_command.call_args_list[0][0][0] == {
        "type": WSType.SUPERVISOR_EVENT,
        "data": {
            "event": WSEvent.SUPERVISOR_UPDATE,
            "update_key": "test",
            "data": {"lorem": "ipsum"},
        },
    }
    assert ha_ws_client.async_send_command.call_args_list[1][0][0] == {
        "type": WSType.SUPERVISOR_EVENT,
        "data": {
            "event": WSEvent.SUPERVISOR_UPDATE,
            "update_key": "info",
            "data": {"state": "running"},
        },
    }

    ha_ws_client.reset_mock()
    await coresys.core.set_state(CoreState.SHUTDOWN)

    await coresys.homeassistant.websocket.async_supervisor_update_event(
        "test", {"lorem": "ipsum"}
    )
    ha_ws_client.async_send_command.assert_not_called()


async def test_send_command_core_not_reachable(
    coresys: CoreSys, ha_ws_client: AsyncMock
):
    """Test async_send_command raises when Core API is not reachable."""
    ha_ws_client.connected = False
    with (
        patch.object(coresys.homeassistant.api, "check_api_state", return_value=False),
        pytest.raises(HomeAssistantWSConnectionError, match="not reachable"),
    ):
        await coresys.homeassistant.websocket.async_send_command({"type": "test"})

    ha_ws_client.async_send_command.assert_not_called()


async def test_fire_and_forget_core_not_reachable(
    coresys: CoreSys, ha_ws_client: AsyncMock
):
    """Test fire-and-forget command silently skips when Core API is not reachable."""
    ha_ws_client.connected = False
    with patch.object(coresys.homeassistant.api, "check_api_state", return_value=False):
        await coresys.homeassistant.websocket._async_send_command({"type": "test"})

    ha_ws_client.async_send_command.assert_not_called()


async def test_send_command_during_shutdown(coresys: CoreSys, ha_ws_client: AsyncMock):
    """Test async_send_command raises during shutdown."""
    await coresys.core.set_state(CoreState.SHUTDOWN)
    with pytest.raises(HomeAssistantWSConnectionError, match="shutting down"):
        await coresys.homeassistant.websocket.async_send_command({"type": "test"})

    ha_ws_client.async_send_command.assert_not_called()


# --- WSClient ---


def _mock_ws_client(messages: list[dict]) -> MagicMock:
    """Create a mock aiohttp WebSocket client that returns messages in sequence."""
    client = AsyncMock(spec=aiohttp.ClientWebSocketResponse)
    client.receive_json = AsyncMock(side_effect=messages)
    client.send_json = AsyncMock()
    client.close = AsyncMock()
    client.closed = False
    return client


@pytest.mark.parametrize(
    ("error", "match"),
    [
        pytest.param(
            aiohttp.ClientConnectorError(MagicMock(), OSError("Connection refused")),
            "Can't connect: Cannot connect to host",
            id="connector",
        ),
        pytest.param(
            aiohttp.WSServerHandshakeError(
                MagicMock(), (), status=503, message="Service Unavailable"
            ),
            "Can't connect: .*Service Unavailable",
            id="handshake",
        ),
        pytest.param(TimeoutError(), "Can't connect: TimeoutError", id="timeout"),
    ],
)
async def test_ws_connect_error(error: Exception, match: str):
    """Test _ws_connect wraps every connect failure as a connection error."""
    session = AsyncMock()
    session.ws_connect = AsyncMock(side_effect=error)

    with pytest.raises(HomeAssistantWSConnectionError, match=match):
        await WSClient._ws_connect(session, "ws://localhost/api/websocket")


async def test_connect_unix_success():
    """Test WSClient.connect succeeds with auth_ok."""
    session = AsyncMock()
    ws = _mock_ws_client([{"type": "auth_ok", "ha_version": "2026.4.0"}])
    session.ws_connect = AsyncMock(return_value=ws)

    client = await WSClient.connect(session, "ws://localhost/api/websocket")
    assert client.ha_version == "2026.4.0"
    assert client.connected is True
    ws.close.assert_not_called()


async def test_connect_unix_unexpected_message():
    """Test WSClient.connect raises and closes on unexpected message."""
    session = AsyncMock()
    ws = _mock_ws_client([{"type": "auth_required", "ha_version": "2026.4.0"}])
    session.ws_connect = AsyncMock(return_value=ws)

    with pytest.raises(HomeAssistantAPIError, match="Expected auth_ok"):
        await WSClient.connect(session, "ws://localhost/api/websocket")
    ws.close.assert_called_once()


async def test_connect_unix_bad_json():
    """Test WSClient.connect wraps ValueError from bad JSON."""
    session = AsyncMock()
    ws = AsyncMock(spec=aiohttp.ClientWebSocketResponse)
    ws.receive_json = AsyncMock(side_effect=ValueError("bad json"))
    ws.close = AsyncMock()
    session.ws_connect = AsyncMock(return_value=ws)

    with pytest.raises(HomeAssistantAPIError, match="Unexpected error"):
        await WSClient.connect(session, "ws://localhost/api/websocket")
    ws.close.assert_called_once()


async def test_connect_with_auth_success():
    """Test WSClient.connect_with_auth succeeds with auth handshake."""
    session = AsyncMock()
    ws = _mock_ws_client(
        [
            {"type": "auth_required", "ha_version": "2026.4.0"},
            {"type": "auth_ok", "ha_version": "2026.4.0"},
        ]
    )
    session.ws_connect = AsyncMock(return_value=ws)

    client = await WSClient.connect_with_auth(
        session, "ws://localhost/api/websocket", "test_token"
    )
    assert client.ha_version == "2026.4.0"
    ws.send_json.assert_called_once()
    ws.close.assert_not_called()


async def test_connect_with_auth_unexpected_first_message():
    """Test connect_with_auth raises on unexpected first message."""
    session = AsyncMock()
    ws = _mock_ws_client([{"type": "auth_ok", "ha_version": "2026.4.0"}])
    session.ws_connect = AsyncMock(return_value=ws)

    with pytest.raises(HomeAssistantAPIError, match="Expected auth_required"):
        await WSClient.connect_with_auth(
            session, "ws://localhost/api/websocket", "test_token"
        )
    ws.close.assert_called_once()


async def test_connect_with_auth_rejected():
    """Test connect_with_auth raises on auth rejection."""
    session = AsyncMock()
    ws = _mock_ws_client(
        [
            {"type": "auth_required", "ha_version": "2026.4.0"},
            {"type": "auth_invalid", "message": "Invalid password"},
        ]
    )
    session.ws_connect = AsyncMock(return_value=ws)

    with pytest.raises(HomeAssistantAPIError, match="AUTH NOT OK"):
        await WSClient.connect_with_auth(
            session, "ws://localhost/api/websocket", "bad_token"
        )
    ws.close.assert_called_once()


async def test_connect_with_auth_missing_key():
    """Test connect_with_auth wraps KeyError from missing keys."""
    session = AsyncMock()
    ws = _mock_ws_client([{"no_type_key": "oops"}])
    session.ws_connect = AsyncMock(return_value=ws)

    with pytest.raises(HomeAssistantAPIError, match="Unexpected error"):
        await WSClient.connect_with_auth(
            session, "ws://localhost/api/websocket", "token"
        )
    ws.close.assert_called_once()


async def test_ws_client_close():
    """Test WSClient.close cancels pending futures and closes connection."""
    ws = AsyncMock(spec=aiohttp.ClientWebSocketResponse)
    ws.closed = False
    ws.close = AsyncMock()

    client = WSClient.__new__(WSClient)
    client.ha_version = "2026.4.0"
    client.client = ws
    client._message_id = 0
    client._futures = {}

    # Add a pending future
    loop = asyncio.get_running_loop()
    future = loop.create_future()
    client._futures[1] = future

    await client.close()

    assert future.done()
    with pytest.raises(HomeAssistantWSConnectionError):
        future.result()
    ws.close.assert_called_once()
