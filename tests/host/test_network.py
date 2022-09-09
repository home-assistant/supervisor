"""Test network manager."""
from ipaddress import IPv4Address, IPv6Address
from unittest.mock import Mock, PropertyMock, patch

import pytest

from supervisor.coresys import CoreSys
from supervisor.dbus.const import ConnectionStateFlags, InterfaceMethod
from supervisor.exceptions import DBusFatalError, HostNotSupportedError
from supervisor.host.const import InterfaceType, WifiMode
from supervisor.host.network import Interface, IpConfig
from supervisor.utils.dbus import DBus


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


async def test_scan_wifi(coresys: CoreSys):
    """Test scanning wifi."""
    with pytest.raises(HostNotSupportedError):
        await coresys.host.network.scan_wifi(coresys.host.network.get("eth0"))

    with patch("supervisor.host.network.asyncio.sleep"):
        aps = await coresys.host.network.scan_wifi(coresys.host.network.get("wlan0"))

    assert len(aps) == 2
    assert aps[0].mac == "E4:57:40:A9:D7:DE"
    assert aps[0].mode == WifiMode.INFRASTRUCTURE
    assert aps[1].mac == "18:4B:0D:23:A1:9C"
    assert aps[1].mode == WifiMode.INFRASTRUCTURE


async def test_scan_wifi_with_failures(coresys: CoreSys, caplog):
    """Test scanning wifi with accesspoint processing failures."""
    # pylint: disable=protected-access
    init_proxy = coresys.dbus.network.dbus._init_proxy

    async def mock_init_proxy(self):
        if self.object_path != "/org/freedesktop/NetworkManager/AccessPoint/99999":
            return await init_proxy()

        raise DBusFatalError("Fail")

    with patch("supervisor.host.network.asyncio.sleep"), patch.object(
        DBus,
        "call_dbus",
        return_value=[
            [
                "/org/freedesktop/NetworkManager/AccessPoint/43099",
                "/org/freedesktop/NetworkManager/AccessPoint/43100",
                "/org/freedesktop/NetworkManager/AccessPoint/99999",
            ]
        ],
    ), patch.object(DBus, "_init_proxy", new=mock_init_proxy):
        aps = await coresys.host.network.scan_wifi(coresys.host.network.get("wlan0"))
        assert len(aps) == 2

    assert "Can't process an AP" in caplog.text
