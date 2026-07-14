"""Test websocket."""

# pylint: disable=import-error
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
from awesomeversion import AwesomeVersion
import pytest

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.exceptions import (
    HomeAssistantAPIError,
    HomeAssistantWSConnectionError,
    HomeAssistantWSError,
)
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


async def test_job_event_uses_legacy_names_with_event_version_1(
    coresys: CoreSys, ha_ws_client: AsyncMock
):
    """Test job events map renamed jobs to legacy names with event version 1."""
    assert ha_ws_client.event_version == 1
    await coresys.homeassistant.websocket.async_supervisor_event_custom(
        WSEvent.JOB, {"data": {"name": "app_manager_update", "progress": 50}}
    )
    ha_ws_client.async_send_command.assert_called_with(
        {
            "type": WSType.SUPERVISOR_EVENT,
            "data": {
                "event": WSEvent.JOB,
                "data": {"name": "addon_manager_update", "progress": 50},
            },
        }
    )


async def test_job_event_uses_new_names_with_event_version_2(
    coresys: CoreSys, ha_ws_client: AsyncMock
):
    """Test job events keep the new job names with event version 2."""
    ha_ws_client.event_version = 2
    await coresys.homeassistant.websocket.async_supervisor_event_custom(
        WSEvent.JOB, {"data": {"name": "app_manager_update", "progress": 50}}
    )
    ha_ws_client.async_send_command.assert_called_with(
        {
            "type": WSType.SUPERVISOR_EVENT,
            "data": {
                "event": WSEvent.JOB,
                "data": {"name": "app_manager_update", "progress": 50},
            },
        }
    )


async def test_connect_negotiates_event_version(coresys: CoreSys):
    """Test the event version is negotiated when a connection is established."""
    ws_client = AsyncMock(connected=True, event_version=1)
    coresys.homeassistant.websocket.client = None
    with (
        patch.object(coresys.homeassistant.api, "check_api_state", return_value=True),
        patch.object(
            coresys.homeassistant.api, "connect_websocket", return_value=ws_client
        ),
    ):
        await coresys.homeassistant.websocket.async_send_command({"type": "test"})

    ws_client.negotiate_event_version.assert_awaited_once()


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


async def test_ws_connect_error():
    """Test _ws_connect wraps ClientConnectorError."""
    session = AsyncMock()
    session.ws_connect = AsyncMock(
        side_effect=aiohttp.ClientConnectorError(
            MagicMock(), OSError("Connection refused")
        )
    )

    with pytest.raises(HomeAssistantWSConnectionError, match="Can't connect"):
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


async def test_negotiate_event_version_core_supported():
    """Test negotiation uses the version Core replies with."""
    client = WSClient(AwesomeVersion("2026.8.0"), _mock_ws_client([]))
    with patch.object(
        WSClient, "async_send_command", return_value={"version": 2}
    ) as send_command:
        await client.negotiate_event_version()

    send_command.assert_called_once_with(
        {"type": WSType.SUPERVISOR_EVENT_VERSION, "supported": [1, 2]}
    )
    assert client.event_version == 2


async def test_negotiate_event_version_core_unsupported():
    """Test negotiation keeps the default version when Core rejects the command."""
    client = WSClient(AwesomeVersion("2026.7.0"), _mock_ws_client([]))
    with patch.object(
        WSClient,
        "async_send_command",
        side_effect=HomeAssistantWSError("Unknown command"),
    ):
        await client.negotiate_event_version()

    assert client.event_version == 1


async def test_negotiate_event_version_invalid_reply():
    """Test negotiation keeps the default version on an invalid reply."""
    client = WSClient(AwesomeVersion("2026.8.0"), _mock_ws_client([]))
    with patch.object(WSClient, "async_send_command", return_value={"version": 99}):
        await client.negotiate_event_version()

    assert client.event_version == 1


async def test_negotiate_event_version_connection_error():
    """Test negotiation propagates connection errors."""
    client = WSClient(AwesomeVersion("2026.8.0"), _mock_ws_client([]))
    with (
        patch.object(
            WSClient,
            "async_send_command",
            side_effect=HomeAssistantWSConnectionError("Connection was closed"),
        ),
        pytest.raises(HomeAssistantWSConnectionError),
    ):
        await client.negotiate_event_version()

    assert client.event_version == 1


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
