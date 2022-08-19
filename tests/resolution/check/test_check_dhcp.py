"""Test Check DHCP."""
from unittest.mock import PropertyMock, patch

import pytest

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.checks.dhcp import CheckDHCP
from supervisor.resolution.const import ContextType, IssueType
from supervisor.resolution.data import Issue


async def test_base(coresys: CoreSys):
    """Test check basics."""
    dhcp = CheckDHCP(coresys)
    assert dhcp.slug == "dhcp"
    assert dhcp.enabled


@pytest.mark.parametrize("config", ["ipv4", "ipv6"])
async def test_check(coresys: CoreSys, config: str):
    """Test check."""
    dhcp = CheckDHCP(coresys)
    coresys.core.state = CoreState.RUNNING

    assert len(coresys.resolution.issues) == 0

    await dhcp.run_check()
    assert len(coresys.resolution.issues) == 0

    with patch(
        f"supervisor.dbus.network.connection.NetworkConnection.{config}",
        new=PropertyMock(return_value=None),
    ):
        await dhcp.run_check()

    assert coresys.resolution.issues == [
        Issue(IssueType.DHCP_FAILURE, ContextType.SYSTEM, "eth0")
    ]


@pytest.mark.parametrize("config", ["ipv4", "ipv6"])
async def test_approve(coresys: CoreSys, config: str):
    """Test check."""
    dhcp = CheckDHCP(coresys)
    coresys.core.state = CoreState.RUNNING

    assert not await dhcp.approve_check("eth0")

    with patch(
        f"supervisor.dbus.network.connection.NetworkConnection.{config}",
        new=PropertyMock(return_value=None),
    ):
        assert await dhcp.approve_check("eth0")


async def test_did_run(coresys: CoreSys):
    """Test that the check ran as expected."""
    dhcp = CheckDHCP(coresys)
    should_run = dhcp.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.checks.dhcp.CheckDHCP.run_check",
        return_value=None,
    ) as check:
        for state in should_run:
            coresys.core.state = state
            await dhcp()
            check.assert_called_once()
            check.reset_mock()

        for state in should_not_run:
            coresys.core.state = state
            await dhcp()
            check.assert_not_called()
            check.reset_mock()
