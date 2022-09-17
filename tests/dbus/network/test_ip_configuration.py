"""Test Network Manager IP configuration object."""

import asyncio
from ipaddress import IPv4Address, IPv6Address

from supervisor.dbus.network import NetworkManager

from tests.common import fire_property_change_signal
from tests.const import TEST_INTERFACE


async def test_ipv4_configuration(network_manager: NetworkManager):
    """Test ipv4 configuration object."""
    ipv4 = network_manager.interfaces[TEST_INTERFACE].connection.ipv4
    assert ipv4.gateway == IPv4Address("192.168.2.1")
    assert ipv4.nameservers == [IPv4Address("192.168.2.2")]

    fire_property_change_signal(ipv4, {"Gateway": "192.168.100.1"})
    await asyncio.sleep(0)
    assert ipv4.gateway == IPv4Address("192.168.100.1")

    fire_property_change_signal(ipv4, {}, ["Gateway"])
    await asyncio.sleep(0)
    assert ipv4.gateway == IPv4Address("192.168.2.1")


async def test_ipv6_configuration(network_manager: NetworkManager):
    """Test ipv4 configuration object."""
    ipv6 = network_manager.interfaces[TEST_INTERFACE].connection.ipv6
    assert ipv6.gateway == IPv6Address("fe80::da58:d7ff:fe00:9c69")
    assert ipv6.nameservers == [
        IPv6Address("2001:1620:2777:1::10"),
        IPv6Address("2001:1620:2777:2::20"),
    ]

    fire_property_change_signal(ipv6, {"Gateway": "2001:1620:2777:1::10"})
    await asyncio.sleep(0)
    assert ipv6.gateway == IPv6Address("2001:1620:2777:1::10")

    fire_property_change_signal(ipv6, {}, ["Gateway"])
    await asyncio.sleep(0)
    assert ipv6.gateway == IPv6Address("fe80::da58:d7ff:fe00:9c69")


async def test_gateway_empty_string(network_manager: NetworkManager):
    """Test empty string in gateway returns None."""
    ipv4 = network_manager.interfaces[TEST_INTERFACE].connection.ipv4
    fire_property_change_signal(ipv4, {"Gateway": ""})
    await asyncio.sleep(0)
    assert ipv4.gateway is None
