"""Test Check Network Interface."""
from unittest.mock import PropertyMock, patch

import pytest

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.dbus.const import ConnectionStateFlags
from supervisor.resolution.checks.network_interface_ipv4 import (
    CheckNetworkInterfaceIPV4,
)
from supervisor.resolution.const import ContextType, IssueType
from supervisor.resolution.data import Issue


async def test_base(coresys: CoreSys):
    """Test check basics."""
    network_interface = CheckNetworkInterfaceIPV4(coresys)
    assert network_interface.slug == "network_interface_ipv4"
    assert network_interface.enabled


@pytest.mark.parametrize(
    "state_flags",
    [
        {ConnectionStateFlags.IP6_READY},
        {ConnectionStateFlags.NONE},
    ],
)
async def test_check(coresys: CoreSys, state_flags: set[ConnectionStateFlags]):
    """Test check."""
    network_interface = CheckNetworkInterfaceIPV4(coresys)
    coresys.core.state = CoreState.RUNNING

    assert len(coresys.resolution.issues) == 0

    await network_interface.run_check()
    assert len(coresys.resolution.issues) == 0

    with patch(
        "supervisor.dbus.network.connection.NetworkConnection.state_flags",
        new=PropertyMock(return_value=state_flags),
    ):
        await network_interface.run_check()

    assert coresys.resolution.issues == [
        Issue(IssueType.IPV4_CONNECTION_PROBLEM, ContextType.SYSTEM, "eth0")
    ]


@pytest.mark.parametrize(
    "state_flags",
    [
        {ConnectionStateFlags.IP6_READY},
        {ConnectionStateFlags.NONE},
    ],
)
async def test_approve(coresys: CoreSys, state_flags: set[ConnectionStateFlags]):
    """Test check."""
    network_interface = CheckNetworkInterfaceIPV4(coresys)
    coresys.core.state = CoreState.RUNNING

    assert not await network_interface.approve_check("eth0")

    with patch(
        "supervisor.dbus.network.connection.NetworkConnection.state_flags",
        new=PropertyMock(return_value=state_flags),
    ):
        assert await network_interface.approve_check("eth0")


async def test_did_run(coresys: CoreSys):
    """Test that the check ran as expected."""
    network_interface = CheckNetworkInterfaceIPV4(coresys)
    should_run = network_interface.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.checks.network_interface_ipv4.CheckNetworkInterfaceIPV4.run_check",
        return_value=None,
    ) as check:
        for state in should_run:
            coresys.core.state = state
            await network_interface()
            check.assert_called_once()
            check.reset_mock()

        for state in should_not_run:
            coresys.core.state = state
            await network_interface()
            check.assert_not_called()
            check.reset_mock()
