"""Test network manager."""
from unittest.mock import Mock, patch

from supervisor.coresys import CoreSys


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

        assert activate_connection.call_count == 1
        assert activate_connection.call_args.args == (
            "/org/freedesktop/NetworkManager/Settings/1",
            "/org/freedesktop/NetworkManager/Devices/1",
        )
