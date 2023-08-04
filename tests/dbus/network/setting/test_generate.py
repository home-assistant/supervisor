"""Test settings generation from interface."""

from supervisor.dbus.network import NetworkManager
from supervisor.dbus.network.setting.generate import get_connection_from_interface
from supervisor.host.network import Interface

from tests.const import TEST_INTERFACE


async def test_get_connection_from_interface(network_manager: NetworkManager):
    """Test network interface."""
    dbus_interface = network_manager.get(TEST_INTERFACE)
    interface = Interface.from_dbus_interface(dbus_interface)
    connection_payload = get_connection_from_interface(interface)

    assert "connection" in connection_payload

    assert "interface-name" not in connection_payload["connection"]
    assert connection_payload["connection"]["type"].value == "802-3-ethernet"
    assert connection_payload["match"]["path"].value == ["platform-ff3f0000.ethernet"]

    assert connection_payload["ipv4"]["method"].value == "auto"
    assert "address-data" not in connection_payload["ipv4"]

    assert connection_payload["ipv6"]["method"].value == "auto"
    assert "address-data" not in connection_payload["ipv6"]
