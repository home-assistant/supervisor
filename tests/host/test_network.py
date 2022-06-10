"""Test network manager."""
from unittest.mock import Mock, patch

from supervisor.coresys import CoreSys
from supervisor.dbus.const import InterfaceMethod
from supervisor.host.const import InterfaceType
from supervisor.host.network import Interface, IpConfig


async def test_load(coresys: CoreSys):
    """Test network manager load."""
    with patch.object(
        coresys.host.sys_dbus.network,
        "activate_connection",
        new=Mock(wraps=coresys.host.sys_dbus.network.activate_connection),
    ) as activate_connection:
        await coresys.host.network.load()

        assert coresys.host.network.connectivity is True

        assert len(coresys.host.network.dns_servers) == 1
        assert str(coresys.host.network.dns_servers[0]) == "192.168.30.1"

        assert len(coresys.host.network.interfaces) == 2
        assert coresys.host.network.interfaces[0].name == "eth0"
        assert coresys.host.network.interfaces[0].enabled is True
        assert coresys.host.network.interfaces[1].name == "wlan0"
        assert coresys.host.network.interfaces[1].enabled is False

        activate_connection.assert_called_once_with(
            "/org/freedesktop/NetworkManager/Settings/1",
            "/org/freedesktop/NetworkManager/Devices/1",
        )


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
            IpConfig(InterfaceMethod.DISABLED, [], None, []),
            IpConfig(InterfaceMethod.DISABLED, [], None, []),
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
