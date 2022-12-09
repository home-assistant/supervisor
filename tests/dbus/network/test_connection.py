"""Test connection object."""

import asyncio

from supervisor.dbus.network import NetworkManager

from tests.common import fire_property_change_signal
from tests.const import TEST_INTERFACE


async def test_old_ipv4_disconnect(network_manager: NetworkManager):
    """Test old ipv4 disconnects on ipv4 change."""
    connection = network_manager.interfaces[TEST_INTERFACE].connection
    ipv4 = connection.ipv4
    assert ipv4.is_connected is True

    fire_property_change_signal(connection, {"Ip4Config": "/"})
    await asyncio.sleep(0)

    assert connection.ipv4 is None
    assert ipv4.is_connected is False


async def test_old_ipv6_disconnect(network_manager: NetworkManager):
    """Test old ipv6 disconnects on ipv6 change."""
    connection = network_manager.interfaces[TEST_INTERFACE].connection
    ipv6 = connection.ipv6
    assert ipv6.is_connected is True

    fire_property_change_signal(connection, {"Ip6Config": "/"})
    await asyncio.sleep(0)

    assert connection.ipv6 is None
    assert ipv6.is_connected is False


async def test_old_settings_disconnect(network_manager: NetworkManager):
    """Test old settings disconnects on settings change."""
    connection = network_manager.interfaces[TEST_INTERFACE].connection
    settings = connection.settings
    assert settings.is_connected is True

    fire_property_change_signal(connection, {"Connection": "/"})
    await asyncio.sleep(0)

    assert connection.settings is None
    assert settings.is_connected is False
