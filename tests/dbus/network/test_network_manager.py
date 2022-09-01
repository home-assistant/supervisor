"""Test NetwrokInterface."""
from unittest.mock import AsyncMock, patch

import pytest

from supervisor.dbus.network import NetworkManager
from supervisor.exceptions import HostNotSupportedError

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


async def test_check_connectivity(network_manager: NetworkManager):
    """Test connectivity check."""
    assert await network_manager.check_connectivity() == 4
    assert await network_manager.check_connectivity(force=True) == 4

    with patch.object(
        type(network_manager.dbus), "call_dbus"
    ) as call_dbus, patch.object(
        type(network_manager.dbus), "get_property"
    ) as get_property:
        await network_manager.check_connectivity()
        call_dbus.assert_not_called()
        get_property.assert_called_once_with(
            "org.freedesktop.NetworkManager", "Connectivity"
        )

        get_property.reset_mock()
        await network_manager.check_connectivity(force=True)

        call_dbus.assert_called_once_with(
            "org.freedesktop.NetworkManager.CheckConnectivity", remove_signature=True
        )
        get_property.assert_not_called()
