"""Test supported features."""

# pylint: disable=protected-access
import asyncio
from unittest.mock import AsyncMock, PropertyMock, patch

from dbus_fast import Variant
import pytest

from supervisor.coresys import CoreSys
from supervisor.plugins.dns import PluginDns

from tests.dbus_service_mocks.network_manager import (
    NetworkManager as NetworkManagerService,
)


@pytest.mark.parametrize("force", [True, False])
async def test_connectivity_not_connected(
    coresys: CoreSys, force: bool, network_manager_service: NetworkManagerService
):
    """Test host unknown connectivity."""
    assert coresys.host.network.connectivity

    network_manager_service.connectivity = 0
    await coresys.host.network.check_connectivity(force=force)
    assert not coresys.host.network.connectivity


async def test_connectivity_connected(
    coresys: CoreSys, network_manager_service: NetworkManagerService
):
    """Test host full connectivity."""
    network_manager_service.CheckConnectivity.calls.clear()

    await coresys.host.network.check_connectivity()
    assert coresys.host.network.connectivity
    assert network_manager_service.CheckConnectivity.calls == []

    await coresys.host.network.check_connectivity(force=True)
    assert coresys.host.network.connectivity
    assert network_manager_service.CheckConnectivity.calls == [()]


@pytest.mark.parametrize("force", [True, False])
async def test_connectivity_events(coresys: CoreSys, force: bool):
    """Test connectivity events."""
    coresys.host.network.connectivity = None
    await asyncio.sleep(0)

    with patch.object(
        type(coresys.homeassistant.websocket), "async_send_message"
    ) as send_message:
        await coresys.host.network.check_connectivity(force=force)
        await asyncio.sleep(0)

        assert coresys.host.network.connectivity is True
        send_message.assert_called_once_with(
            {
                "type": "supervisor/event",
                "data": {
                    "event": "supervisor_update",
                    "update_key": "network",
                    "data": {"host_internet": True},
                },
            }
        )

        send_message.reset_mock()
        with patch.object(
            type(coresys.dbus.network),
            "connectivity_enabled",
            new=PropertyMock(return_value=False),
        ):
            await coresys.host.network.check_connectivity(force=force)
            await asyncio.sleep(0)

            assert coresys.host.network.connectivity is None
            send_message.assert_called_once_with(
                {
                    "type": "supervisor/event",
                    "data": {
                        "event": "supervisor_update",
                        "update_key": "network",
                        "data": {"host_internet": None},
                    },
                }
            )


async def test_dns_restart_on_dns_configuration_change(
    coresys: CoreSys, dns_manager_service
):
    """Test dns plugin is restarted when DNS configuration changes."""
    await coresys.host.network.load()
    with (
        patch.object(PluginDns, "restart") as restart,
        patch.object(
            PluginDns, "is_running", new_callable=AsyncMock, return_value=True
        ),
    ):
        # Test that non-Configuration changes don't trigger restart
        await coresys.host.network._check_dns_changed(
            "org.freedesktop.NetworkManager.DnsManager", {"Mode": "default"}, []
        )
        restart.assert_not_called()

        # Test that Configuration changes trigger restart
        configuration = [
            {
                "nameservers": Variant("as", ["192.168.2.2"]),
                "domains": Variant("as", ["lan"]),
                "interface": Variant("s", "eth0"),
                "priority": Variant("i", 100),
                "vpn": Variant("b", False),
            }
        ]

        with patch.object(PluginDns, "notify_locals_changed") as notify_locals_changed:
            await coresys.host.network._check_dns_changed(
                "org.freedesktop.NetworkManager.DnsManager",
                {"Configuration": configuration},
                [],
            )
            notify_locals_changed.assert_called_once()

        restart.reset_mock()
        # Test that DNS plugin is not running (should not restart)
        with patch.object(
            PluginDns, "is_running", new_callable=AsyncMock, return_value=False
        ):
            await coresys.host.network._check_dns_changed(
                "org.freedesktop.NetworkManager.DnsManager",
                {"Configuration": configuration},
                [],
            )
            restart.assert_not_called()
