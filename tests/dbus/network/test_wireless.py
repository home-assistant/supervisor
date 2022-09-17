"""Test Network Manager Wireless object."""
import asyncio

from supervisor.dbus.network import NetworkManager

from tests.common import fire_property_change_signal


async def test_wireless(network_manager: NetworkManager):
    """Test wireless properties."""
    assert network_manager.interfaces["wlan0"].wireless.active is None

    fire_property_change_signal(
        network_manager.interfaces["wlan0"].wireless,
        {"ActiveAccessPoint": "/org/freedesktop/NetworkManager/AccessPoint/43099"},
    )
    await asyncio.sleep(0)
    assert (
        network_manager.interfaces["wlan0"].wireless.active.mac == "E4:57:40:A9:D7:DE"
    )

    fire_property_change_signal(
        network_manager.interfaces["wlan0"].wireless, {}, ["ActiveAccessPoint"]
    )
    await asyncio.sleep(0)
    assert network_manager.interfaces["wlan0"].wireless.active is None


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
