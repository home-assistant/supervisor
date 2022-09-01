"""Test supported features."""
# pylint: disable=protected-access
import asyncio
from unittest.mock import PropertyMock, patch

import pytest

from supervisor.coresys import CoreSys


async def test_connectivity_not_connected(coresys: CoreSys):
    """Test host unknown connectivity."""
    with patch("supervisor.utils.dbus.DBus.get_property", return_value=0):
        await coresys.host.network.check_connectivity()
        assert not coresys.host.network.connectivity

    with patch("supervisor.utils.dbus.DBus.call_dbus", return_value=[0]):
        await coresys.host.network.check_connectivity(force=True)
        assert not coresys.host.network.connectivity


async def test_connectivity_connected(coresys: CoreSys):
    """Test host full connectivity."""
    # Variation on above since our default fixture for each of these returns 4
    with patch(
        "supervisor.utils.dbus.DBus.get_property", return_value=4
    ) as get_property, patch(
        "supervisor.utils.dbus.DBus.call_dbus", return_value=[4]
    ) as call_dbus:
        await coresys.host.network.check_connectivity()
        assert coresys.host.network.connectivity
        get_property.assert_called_once()
        call_dbus.assert_not_called()

        get_property.reset_mock()
        await coresys.host.network.check_connectivity(force=True)
        assert coresys.host.network.connectivity
        get_property.assert_not_called()
        call_dbus.assert_called_once()


@pytest.mark.parametrize("force", [True, False])
async def test_connectivity_events(coresys: CoreSys, force: bool):
    """Test connectivity events."""
    coresys.host.network.connectivity = None
    await asyncio.sleep(0)

    with patch.object(
        type(coresys.homeassistant.websocket), "async_send_message"
    ) as send_message:
        await coresys.host.network.check_connectivity(force=force)
        await asyncio.sleep(0)

        assert coresys.host.network.connectivity is True
        send_message.assert_called_once_with(
            {
                "type": "supervisor/event",
                "data": {
                    "event": "supervisor_update",
                    "update_key": "network",
                    "data": {"host_internet": True},
                },
            }
        )

        send_message.reset_mock()
        with patch.object(
            type(coresys.dbus.network),
            "connectivity_enabled",
            new=PropertyMock(return_value=False),
        ):
            await coresys.host.network.check_connectivity(force=force)
            await asyncio.sleep(0)

            assert coresys.host.network.connectivity is None
            send_message.assert_called_once_with(
                {
                    "type": "supervisor/event",
                    "data": {
                        "event": "supervisor_update",
                        "update_key": "network",
                        "data": {"host_internet": None},
                    },
                }
            )
