"""Test NetwrokInterface."""
import pytest

from supervisor.dbus.network.interface import NetworkInterface


@pytest.mark.asyncio
async def test_network_interface(network_manager):
    """Test network interface."""
    interface = NetworkInterface()
    await interface.connect()
