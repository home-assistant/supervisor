"""Test NetworkWireless AP object."""
from supervisor.dbus.network.accesspoint import NetworkWirelessAP


async def test_accesspoint(dbus: list[str]):
    """Test accesspoint."""
    wireless_ap = NetworkWirelessAP("/org/freedesktop/NetworkManager/AccessPoint/43099")

    assert wireless_ap.mac is None
    assert wireless_ap.mode is None

    await wireless_ap.connect()

    assert wireless_ap.mac == "E4:57:40:A9:D7:DE"
    assert wireless_ap.mode == 2
