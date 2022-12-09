"""Test Network Manager Connection Settings Profile Manager."""
from supervisor.dbus.network import NetworkManager

from tests.dbus.network.setting.test_init import SETTINGS_WITH_SIGNATURE


async def test_add_connection(network_manager: NetworkManager, dbus: list[str]):
    """Test adding settings connection."""
    dbus.clear()
    settings = await network_manager.settings.add_connection(SETTINGS_WITH_SIGNATURE)
    assert settings.connection.uuid == "0c23631e-2118-355c-bbb0-8943229cb0d6"
    assert settings.ipv4.method == "auto"
    assert dbus == [
        "/org/freedesktop/NetworkManager/Settings-org.freedesktop.NetworkManager.Settings.AddConnection",
        "/org/freedesktop/NetworkManager/Settings/1-org.freedesktop.NetworkManager.Settings.Connection.GetSettings",
    ]


async def test_reload_connections(network_manager: NetworkManager, dbus: list[str]):
    """Test reload connections."""
    dbus.clear()
    assert await network_manager.settings.reload_connections() is True
    assert dbus == [
        "/org/freedesktop/NetworkManager/Settings-org.freedesktop.NetworkManager.Settings.ReloadConnections"
    ]
