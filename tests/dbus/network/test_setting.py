"""Test NetwrokInterface."""
from ipaddress import IPv4Address, IPv4Interface, IPv6Address, IPv6Interface

import pytest

from supervisor.dbus.const import DeviceType, InterfaceMethod
from supervisor.dbus.network import NetworkManager
from supervisor.host.network import Interface

from tests.const import TEST_INTERFACE, TEST_INTERFACE_WLAN

from supervisor.dbus.network.setting.generate import get_connection_from_interface


@pytest.mark.asyncio
async def test_get_connection_from_interface(network_manager: NetworkManager):
    """Test network interface."""
    dbus_interface = network_manager.interfaces[TEST_INTERFACE]
    interface = Interface.from_dbus_interface(dbus_interface)
    connection_payload = get_connection_from_interface(interface)

    assert "connection" in connection_payload

    assert connection_payload["connection"]["interface-name"].value == TEST_INTERFACE
    assert connection_payload["connection"]["type"].value == "802-3-ethernet"

    assert connection_payload["ipv4"]["method"].value == "auto"
    assert "address-data" not in connection_payload["ipv4"]

    assert connection_payload["ipv6"]["method"].value == "auto"
    assert "address-data" not in connection_payload["ipv6"]


@pytest.mark.asyncio
async def test_network_interface_wlan(network_manager: NetworkManager):
    """Test network interface."""
    interface = network_manager.interfaces[TEST_INTERFACE_WLAN]
    assert interface.name == TEST_INTERFACE_WLAN
    assert interface.type == DeviceType.WIRELESS
