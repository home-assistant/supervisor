"""Test NetwrokInterface."""
import pytest

from supervisor.dbus.network import NetworkManager

from tests.const import TEST_INTERFACE


@pytest.mark.asyncio
async def test_network_manager(network_manager: NetworkManager):
    """Test network manager update."""
    assert TEST_INTERFACE in network_manager.interfaces
