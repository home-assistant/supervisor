"""Test Network Manager Wireless object."""
from supervisor.dbus.network import NetworkManager


async def test_request_scan(network_manager: NetworkManager, dbus: list[str]):
    """Test request scan."""
    dbus.clear()
    assert await network_manager.interfaces["wlan0"].wireless.request_scan() is None
    assert dbus == [
        "/org/freedesktop/NetworkManager/Devices/3-org.freedesktop.NetworkManager.Device.Wireless.RequestScan"
    ]


async def test_get_all_access_points(network_manager: NetworkManager, dbus: list[str]):
    """Test get all access points."""
    dbus.clear()
    accesspoints = await network_manager.interfaces[
        "wlan0"
    ].wireless.get_all_accesspoints()
    assert len(accesspoints) == 2
    assert accesspoints[0].mac == "E4:57:40:A9:D7:DE"
    assert accesspoints[0].mode == 2
    assert accesspoints[1].mac == "18:4B:0D:23:A1:9C"
    assert accesspoints[1].mode == 2
    assert dbus == [
        "/org/freedesktop/NetworkManager/Devices/3-org.freedesktop.NetworkManager.Device.Wireless.GetAllAccessPoints"
    ]
