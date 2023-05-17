"""Test supported features."""
# pylint: disable=protected-access
import asyncio
from unittest.mock import PropertyMock, patch

import pytest

from supervisor.coresys import CoreSys

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
    assert network_manager_service.CheckConnectivity.calls == [tuple()]


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
