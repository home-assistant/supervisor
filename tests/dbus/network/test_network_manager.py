"""Test NetwrokInterface."""
from unittest.mock import AsyncMock, patch

import pytest

from supervisor.coresys import CoreSys
from supervisor.dbus.network import NetworkManager
from supervisor.exceptions import HostNetworkError, HostNotSupportedError

from tests.const import TEST_INTERFACE

# pylint: disable=protected-access


@pytest.mark.asyncio
async def test_network_manager(network_manager: NetworkManager):
    """Test network manager update."""
    assert TEST_INTERFACE in network_manager.interfaces


@pytest.mark.asyncio
async def test_network_manager_version(network_manager: NetworkManager):
    """Test if version validate work."""
    await network_manager._validate_version()
    assert network_manager.version == "1.22.10"

    network_manager.dbus.get_properties = AsyncMock(return_value={"Version": "1.13.9"})
    with pytest.raises(HostNotSupportedError):
        await network_manager._validate_version()
    assert network_manager.version == "1.13.9"


@pytest.mark.asyncio
async def test_disabling_ipv6(coresys: CoreSys, network_manager: NetworkManager):
    """Test disabling IPv6."""
    test_interface = coresys.host.network.get(TEST_INTERFACE)
    test_interface.ipv6.method = "disabled"
    network_manager.dbus.get_properties = AsyncMock(return_value={"Version": "1.14.6"})
    await network_manager._validate_version()
    with pytest.raises(HostNetworkError):
        await coresys.host.network.apply_changes(test_interface)

    assert coresys.host.network.get(TEST_INTERFACE).ipv6.method == "auto"
    network_manager.dbus.get_properties = AsyncMock(return_value={"Version": "1.22.1"})
    await network_manager._validate_version()
    with patch(
        "supervisor.dbus.network.NetworkManager.update", side_effect=AsyncMock()
    ), patch(
        "supervisor.dbus.network.NetworkManager.connectivity_enabled", return_value=True
    ):
        await coresys.host.network.apply_changes(test_interface)
