"""Test supported features."""
# pylint: disable=protected-access
import asyncio
from unittest.mock import PropertyMock, patch

import pytest

from supervisor.coresys import CoreSys


async def test_connectivity_not_connected(coresys: CoreSys):
    """Test host unknown connectivity."""
    with patch("supervisor.utils.dbus.DBus.call_dbus", return_value=0):
        await coresys.host.network.check_connectivity()
        assert not coresys.host.network.connectivity

        await coresys.host.network.check_connectivity(force=True)
        assert not coresys.host.network.connectivity


async def test_connectivity_connected(coresys: CoreSys, dbus: list[str]):
    """Test host full connectivity."""
    dbus.clear()
    await coresys.host.network.check_connectivity()
    assert coresys.host.network.connectivity
    assert dbus == [
        "/org/freedesktop/NetworkManager-org.freedesktop.NetworkManager.Connectivity"
    ]

    dbus.clear()
    await coresys.host.network.check_connectivity(force=True)
    assert coresys.host.network.connectivity
    assert dbus == [
        "/org/freedesktop/NetworkManager-org.freedesktop.NetworkManager.CheckConnectivity"
    ]


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
