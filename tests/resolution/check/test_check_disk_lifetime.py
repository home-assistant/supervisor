"""Test check disk lifetime fixup."""

# pylint: disable=import-error,protected-access
from unittest.mock import PropertyMock, patch

import pytest

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.checks.disk_lifetime import CheckDiskLifetime
from supervisor.resolution.const import ContextType, IssueType
from supervisor.resolution.data import Issue


async def test_base(coresys: CoreSys):
    """Test check basics."""
    disk_lifetime = CheckDiskLifetime(coresys)
    assert disk_lifetime.slug == "disk_lifetime"
    assert disk_lifetime.enabled


async def test_check_no_data_disk(coresys: CoreSys):
    """Test check when no data disk is available."""
    disk_lifetime = CheckDiskLifetime(coresys)
    await coresys.core.set_state(CoreState.RUNNING)

    # Mock no data disk
    with patch.object(
        type(coresys.dbus.agent.datadisk),
        "current_device",
        new=PropertyMock(return_value=None),
    ):
        await disk_lifetime()

    assert len(coresys.resolution.issues) == 0


@pytest.mark.parametrize(
    ("lifetime", "has_issue"),
    [(0.0, False), (85.0, False), (90.0, True), (95.0, True), (None, False)],
)
async def test_check_lifetime_threshold(
    coresys: CoreSys, lifetime: float | None, has_issue: bool
):
    """Test check when disk lifetime at thresholds."""
    disk_lifetime = CheckDiskLifetime(coresys)
    await coresys.core.set_state(CoreState.RUNNING)

    # Mock data disk with lifetime
    with (
        patch.object(
            type(coresys.dbus.agent.datadisk),
            "current_device",
            new=PropertyMock(return_value="/dev/sda1"),
        ),
        patch.object(
            coresys.hardware.disk,
            "get_disk_life_time",
            return_value=lifetime,
        ),
    ):
        await disk_lifetime()

    assert (
        Issue(IssueType.DISK_LIFETIME, ContextType.SYSTEM) in coresys.resolution.issues
    ) is has_issue


async def test_approve_no_data_disk(coresys: CoreSys):
    """Test approve when no data disk is available."""
    disk_lifetime = CheckDiskLifetime(coresys)

    # Mock no data disk
    with patch.object(
        type(coresys.dbus.agent.datadisk),
        "current_device",
        new=PropertyMock(return_value=None),
    ):
        assert not await disk_lifetime.approve_check()


@pytest.mark.parametrize(
    ("lifetime", "approved"),
    [(0.0, False), (85.0, False), (90.0, True), (95.0, True), (None, False)],
)
async def test_approve_check_lifetime_threshold(
    coresys: CoreSys, lifetime: float | None, approved: bool
):
    """Test approve check when disk lifetime at thresholds."""
    disk_lifetime = CheckDiskLifetime(coresys)
    await coresys.core.set_state(CoreState.RUNNING)

    # Mock data disk with lifetime
    with (
        patch.object(
            type(coresys.dbus.agent.datadisk),
            "current_device",
            new=PropertyMock(return_value="/dev/sda1"),
        ),
        patch.object(
            coresys.hardware.disk,
            "get_disk_life_time",
            return_value=lifetime,
        ),
    ):
        assert await disk_lifetime.approve_check() is approved


async def test_did_run(coresys: CoreSys):
    """Test that the check ran as expected."""
    disk_lifetime = CheckDiskLifetime(coresys)
    should_run = disk_lifetime.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert len(should_run) != 0
    assert len(should_not_run) != 0

    with patch(
        "supervisor.resolution.checks.disk_lifetime.CheckDiskLifetime.run_check",
        return_value=None,
    ) as check:
        for state in should_run:
            await coresys.core.set_state(state)
            await disk_lifetime()
            check.assert_called_once()
            check.reset_mock()

        for state in should_not_run:
            await coresys.core.set_state(state)
            await disk_lifetime()
            check.assert_not_called()
            check.reset_mock()
