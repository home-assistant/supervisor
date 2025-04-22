"""Test websocket."""

# pylint: disable=import-error
import asyncio
import logging
from unittest.mock import AsyncMock

from awesomeversion import AwesomeVersion

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.homeassistant.const import WSEvent, WSType


async def test_send_command(coresys: CoreSys, ha_ws_client: AsyncMock):
    """Test websocket error on listen."""
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


async def test_send_command_old_core_version(
    coresys: CoreSys, ha_ws_client: AsyncMock, caplog
):
    """Test websocket error on listen."""
    caplog.set_level(logging.INFO)
    ha_ws_client.ha_version = AwesomeVersion("1970.1.1")

    await coresys.homeassistant.websocket.async_send_command(
        {"type": "supervisor/event"}
    )

    assert (
        "WebSocket command supervisor/event is not supported until core-2021.2.4"
        in caplog.text
    )

    await coresys.homeassistant.websocket.async_supervisor_update_event(
        "test", {"lorem": "ipsum"}
    )
    ha_ws_client.async_send_command.assert_not_called()


async def test_send_message_during_startup(coresys: CoreSys, ha_ws_client: AsyncMock):
    """Test websocket messages queue during startup."""
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
