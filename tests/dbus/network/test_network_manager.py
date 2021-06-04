"""Test NetwrokInterface."""
from unittest.mock import AsyncMock, patch

import pytest

from supervisor.coresys import CoreSys
from supervisor.dbus.const import InterfaceMethod
from supervisor.dbus.network import NetworkManager
from supervisor.exceptions import HostNotSupportedError
from supervisor.utils.gdbus import DBus

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
    test_interface.enabled = True

    with patch(
        "supervisor.dbus.network.NetworkManager.add_and_activate_connection",
        side_effect=AsyncMock(),
    ) as add_and_activate_connection_mock, patch(
        "supervisor.dbus.network.NetworkManager.update", side_effect=AsyncMock()
    ), patch(
        "supervisor.dbus.network.NetworkManager.connectivity_enabled",
        return_value=True,
    ):
        network_manager.dbus.get_properties = AsyncMock(
            return_value={"Version": "1.14.6"}
        )
        await network_manager._validate_version()

        assert coresys.dbus.network.version == "1.14.6"
        test_interface.ipv6.method = InterfaceMethod.DISABLED
        await coresys.host.network.apply_changes(test_interface)
        payload = DBus.parse_gvariant(
            add_and_activate_connection_mock.call_args.args[0]
        )
        assert payload["ipv6"]["method"] == InterfaceMethod.LINK_LOCAL

        network_manager.dbus.get_properties = AsyncMock(
            return_value={"Version": "1.22.1"}
        )
        await network_manager._validate_version()

        assert coresys.dbus.network.version == "1.22.1"
        test_interface.ipv6.method = InterfaceMethod.DISABLED
        await coresys.host.network.apply_changes(test_interface)
        payload = DBus.parse_gvariant(
            add_and_activate_connection_mock.call_args.args[0]
        )
        assert payload["ipv6"]["method"] == InterfaceMethod.DISABLED
