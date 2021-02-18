"""Test websocket."""
# pylint: disable=protected-access, import-error
from awesomeversion import AwesomeVersion
import pytest

from supervisor.coresys import CoreSys
from supervisor.exceptions import HomeAssistantWSNotSupported


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
            "type": "supervisor/event",
            "data": {
                "event": "supervisor-update",
                "update_key": "test",
                "data": {"lorem": "ipsum"},
            },
        }
    )


async def test_send_command_old_core_version(coresys: CoreSys):
    """Test websocket error on listen."""
    client = coresys.homeassistant.websocket._client
    client.ha_version = AwesomeVersion("1970.1.1")

    with pytest.raises(HomeAssistantWSNotSupported):
        await coresys.homeassistant.websocket.async_send_command({"type": "test"})

    await coresys.homeassistant.websocket.async_supervisor_update_event(
        "test", {"lorem": "ipsum"}
    )
    client.async_send_command.assert_not_called()
