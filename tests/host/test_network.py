"""Test network manager."""
import asyncio
from ipaddress import IPv4Address, IPv6Address
from unittest.mock import Mock, PropertyMock, patch

import pytest

from supervisor.coresys import CoreSys
from supervisor.dbus.const import ConnectionStateFlags, InterfaceMethod
from supervisor.host.const import InterfaceType
from supervisor.host.network import Interface, IpConfig


async def test_load(coresys: CoreSys):
    """Test network manager load."""
    with patch.object(
        type(coresys.host.sys_dbus.network),
        "activate_connection",
        new=Mock(wraps=coresys.host.sys_dbus.network.activate_connection),
    ) as activate_connection, patch.object(
        type(coresys.host.sys_dbus.network),
        "check_connectivity",
        new=Mock(wraps=coresys.host.sys_dbus.network.check_connectivity),
    ) as check_connectivity:
        await coresys.host.network.load()

        assert coresys.host.network.connectivity is True

        assert len(coresys.host.network.dns_servers) == 1
        assert str(coresys.host.network.dns_servers[0]) == "192.168.30.1"

        assert len(coresys.host.network.interfaces) == 2
        assert coresys.host.network.interfaces[0].name == "eth0"
        assert coresys.host.network.interfaces[0].enabled is True
        assert coresys.host.network.interfaces[0].ipv4.method == InterfaceMethod.AUTO
        assert coresys.host.network.interfaces[0].ipv4.gateway == IPv4Address(
            "192.168.2.1"
        )
        assert coresys.host.network.interfaces[0].ipv4.ready is True
        assert coresys.host.network.interfaces[0].ipv6.method == InterfaceMethod.AUTO
        assert coresys.host.network.interfaces[0].ipv6.gateway == IPv6Address(
            "fe80::da58:d7ff:fe00:9c69"
        )
        assert coresys.host.network.interfaces[0].ipv6.ready is True
        assert coresys.host.network.interfaces[1].name == "wlan0"
        assert coresys.host.network.interfaces[1].enabled is False

        activate_connection.assert_called_once_with(
            "/org/freedesktop/NetworkManager/Settings/1",
            "/org/freedesktop/NetworkManager/Devices/1",
        )

        assert check_connectivity.call_count == 2
        assert check_connectivity.call_args_list[0][1] == {"force": False}
        assert check_connectivity.call_args_list[1][1] == {"force": False}


async def test_load_with_disabled_methods(coresys: CoreSys):
    """Test load does not disable methods of interfaces."""
    with patch(
        "supervisor.host.network.Interface.from_dbus_interface",
        return_value=Interface(
            "eth0",
            True,
            False,
            False,
            InterfaceType.ETHERNET,
            IpConfig(InterfaceMethod.DISABLED, [], None, [], False),
            IpConfig(InterfaceMethod.DISABLED, [], None, [], False),
            None,
            None,
        ),
    ), patch.object(
        coresys.host.sys_dbus.network,
        "activate_connection",
        new=Mock(wraps=coresys.host.sys_dbus.network.activate_connection),
    ) as activate_connection:
        await coresys.host.network.load()

        activate_connection.assert_not_called()


async def test_load_with_network_connection_issues(coresys: CoreSys):
    """Test load does not update interfaces with network connection issues."""
    with patch(
        "supervisor.dbus.network.connection.NetworkConnection.state_flags",
        new=PropertyMock(return_value={ConnectionStateFlags.IP6_READY}),
    ), patch(
        "supervisor.dbus.network.connection.NetworkConnection.ipv4",
        new=PropertyMock(return_value=None),
    ), patch.object(
        coresys.host.sys_dbus.network,
        "activate_connection",
        new=Mock(wraps=coresys.host.sys_dbus.network.activate_connection),
    ) as activate_connection:
        await coresys.host.network.load()

        activate_connection.assert_not_called()

        assert len(coresys.host.network.interfaces) == 2
        assert coresys.host.network.interfaces[0].name == "eth0"
        assert coresys.host.network.interfaces[0].enabled is True
        assert coresys.host.network.interfaces[0].ipv4.method == InterfaceMethod.AUTO
        assert coresys.host.network.interfaces[0].ipv4.gateway is None
        assert coresys.host.network.interfaces[0].ipv6.method == InterfaceMethod.AUTO
        assert coresys.host.network.interfaces[0].ipv6.gateway == IPv6Address(
            "fe80::da58:d7ff:fe00:9c69"
        )


@pytest.mark.parametrize("force", [True, False])
async def test_check_connectivity(coresys: CoreSys, force: bool):
    """Test check connectivity."""
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
