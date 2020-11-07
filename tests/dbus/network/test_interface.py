"""Test NetwrokInterface."""
from ipaddress import IPv4Address, IPv4Interface, IPv6Address, IPv6Interface

import pytest

from supervisor.dbus.const import DeviceType, InterfaceMethod
from supervisor.dbus.network import NetworkManager

from tests.const import TEST_INTERFACE, TEST_INTERFACE_WLAN


@pytest.mark.asyncio
async def test_network_interface_ethernet(network_manager: NetworkManager):
    """Test network interface."""
    interface = network_manager.interfaces[TEST_INTERFACE]
    assert interface.name == TEST_INTERFACE
    assert interface.type == DeviceType.ETHERNET
    assert interface.connection.state == 2
    assert interface.connection.uuid == "0c23631e-2118-355c-bbb0-8943229cb0d6"

    assert interface.connection.ipv4.address == [IPv4Interface("192.168.2.148/24")]
    assert interface.connection.ipv6.address == [
        IPv6Interface("2a03:169:3df5:0:6be9:2588:b26a:a679/64"),
        IPv6Interface("fd14:949b:c9cc:0:522b:8108:8ff8:cca3/64"),
        IPv6Interface("2a03:169:3df5::2f1/128"),
        IPv6Interface("fd14:949b:c9cc::2f1/128"),
        IPv6Interface("fe80::ffe3:319e:c630:9f51/64"),
    ]

    assert interface.connection.ipv4.gateway == IPv4Address("192.168.2.1")
    assert interface.connection.ipv6.gateway == IPv6Address("fe80::da58:d7ff:fe00:9c69")

    assert interface.connection.ipv4.nameservers == [IPv4Address("192.168.2.2")]
    assert interface.connection.ipv6.nameservers == [
        IPv6Address("2001:1620:2777:1::10"),
        IPv6Address("2001:1620:2777:2::20"),
    ]

    assert interface.settings.ipv4.method == InterfaceMethod.AUTO
    assert interface.settings.ipv6.method == InterfaceMethod.AUTO
    assert interface.settings.connection.id == "Wired connection 1"


@pytest.mark.asyncio
async def test_network_interface_wlan(network_manager: NetworkManager):
    """Test network interface."""
    interface = network_manager.interfaces[TEST_INTERFACE_WLAN]
    assert interface.name == TEST_INTERFACE_WLAN
    assert interface.type == DeviceType.WIRELESS
