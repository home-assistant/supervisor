"""Test NetwrokInterface."""
import pytest

from supervisor.dbus.network import NetworkManager

from tests.const import TEST_INTERFACE


@pytest.mark.asyncio
async def test_network_interface(network_manager: NetworkManager):
    """Test network interface."""
    interface = network_manager.interfaces[TEST_INTERFACE]
    assert interface.name == TEST_INTERFACE
    assert interface.connection.state == 2
    assert interface.connection.uuid == "0c23631e-2118-355c-bbb0-8943229cb0d6"
