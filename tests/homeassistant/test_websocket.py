"""Test websocket."""

# pylint: disable=import-error
import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.exceptions import HomeAssistantWSError
from supervisor.homeassistant.const import WSEvent, WSType


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
        pytest.raises(HomeAssistantWSError, match="not reachable"),
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
    with pytest.raises(HomeAssistantWSError, match="shutting down"):
        await coresys.homeassistant.websocket.async_send_command({"type": "test"})

    ha_ws_client.async_send_command.assert_not_called()
