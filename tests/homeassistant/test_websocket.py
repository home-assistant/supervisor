"""Test websocket."""
# pylint: disable=protected-access, import-error
import logging

from awesomeversion import AwesomeVersion

from supervisor.coresys import CoreSys
from supervisor.homeassistant.const import WSEvent, WSType


async def test_send_command(coresys: CoreSys):
    """Test websocket error on listen."""
    client = coresys.homeassistant.websocket._client
    await coresys.homeassistant.websocket.async_send_command({"type": "test"})
    client.async_send_command.assert_called_with({"type": "test"})

    await coresys.homeassistant.websocket.async_supervisor_update_event(
        "test", {"lorem": "ipsum"}
    )
    client.async_send_command.assert_called_with(
        {
            "type": WSType.SUPERVISOR_EVENT,
            "data": {
                "event": WSEvent.SUPERVISOR_UPDATE,
                "update_key": "test",
                "data": {"lorem": "ipsum"},
            },
        }
    )


async def test_send_command_old_core_version(coresys: CoreSys, caplog):
    """Test websocket error on listen."""
    caplog.set_level(logging.INFO)
    client = coresys.homeassistant.websocket._client
    client.ha_version = AwesomeVersion("1970.1.1")

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
    client.async_send_command.assert_not_called()
