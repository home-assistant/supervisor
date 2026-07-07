"""Test check for systemd unit failures."""

# pylint: disable=protected-access
from datetime import datetime
from typing import cast
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.jobs.decorator import Job
from supervisor.resolution.checks.systemd_unit_failure import (
    DATA_FSCK_UNIT,
    FIREWALL_SERVICE,
    NM_WAIT_ONLINE_SERVICE,
    OS_FSCK_UNITS,
    CheckSystemdUnitFailure,
)
from supervisor.resolution.const import ContextType, IssueType, UnhealthyReason
from supervisor.resolution.data import Issue


@pytest.fixture(autouse=True)
def reset_systemd_unit_failure_throttle() -> None:
    """Reset throttle state for deterministic tests."""
    job = cast(
        Job,
        CheckSystemdUnitFailure._refresh_failed_units_cache.__closure__[
            1
        ].cell_contents,
    )
    job._last_call.clear()
    job.set_last_call(datetime.min)


async def test_base(coresys: CoreSys):
    """Test check basics."""
    systemd_unit_failure = CheckSystemdUnitFailure(coresys)
    assert systemd_unit_failure.slug == "systemd_unit_failure"
    assert systemd_unit_failure.enabled
    assert systemd_unit_failure.issue == IssueType.SYSTEMD_UNIT_FAILED
    assert systemd_unit_failure.context == ContextType.SYSTEM
    assert systemd_unit_failure.states == [CoreState.SETUP]


@pytest.mark.usefixtures("os_available")
async def test_check_creates_issue_and_captures_message(
    coresys: CoreSys, capture_message: Mock
):
    """Test check creates issue and captures a sentry message."""
    systemd_unit_failure = CheckSystemdUnitFailure(coresys)

    with patch.object(
        coresys.dbus.systemd,
        "list_units_filtered",
        new_callable=AsyncMock,
        return_value=[("example.service",)],
    ):
        await systemd_unit_failure.run_check()

    assert len(coresys.resolution.issues) == 1
    assert coresys.resolution.issues[0] == Issue(
        IssueType.SYSTEMD_UNIT_FAILED,
        ContextType.SYSTEM,
        reference="example.service",
    )
    assert len(coresys.resolution.suggestions) == 2
    capture_message.assert_called_once_with(
        "Systemd unit failed: example.service", level="error"
    )


@pytest.mark.usefixtures("os_available")
async def test_mount_unit_failures_ignored(coresys: CoreSys, capture_message: Mock):
    """Test mount unit failures are ignored."""
    systemd_unit_failure = CheckSystemdUnitFailure(coresys)
    coresys.mounts._mounts = {"test": MagicMock(unit_name="mnt-data.mount")}
    coresys.mounts._bound_mounts = {}

    with patch.object(
        coresys.dbus.systemd,
        "list_units_filtered",
        new_callable=AsyncMock,
        return_value=[("mnt-data.mount",)],
    ):
        await systemd_unit_failure.run_check()

    assert not coresys.resolution.issues
    assert not coresys.resolution.suggestions
    capture_message.assert_not_called()


@pytest.mark.usefixtures("os_available")
async def test_firewall_service_failure_ignored(
    coresys: CoreSys, capture_message: Mock
):
    """Test firewall service failure is ignored."""
    systemd_unit_failure = CheckSystemdUnitFailure(coresys)

    with patch.object(
        coresys.dbus.systemd,
        "list_units_filtered",
        new_callable=AsyncMock,
        return_value=[(FIREWALL_SERVICE,)],
    ):
        await systemd_unit_failure.run_check()

    assert not coresys.resolution.issues
    assert not coresys.resolution.suggestions
    capture_message.assert_not_called()


async def test_nm_wait_online_failure_ignored(coresys: CoreSys, capture_message: Mock):
    """Test NetworkManager-wait-online failure is ignored."""
    systemd_unit_failure = CheckSystemdUnitFailure(coresys)

    with patch.object(
        coresys.dbus.systemd,
        "list_units_filtered",
        new_callable=AsyncMock,
        return_value=[(NM_WAIT_ONLINE_SERVICE,)],
    ):
        await systemd_unit_failure.run_check()

    assert not coresys.resolution.issues
    assert not coresys.resolution.suggestions
    capture_message.assert_not_called()


async def test_check_skipped_on_supervised(coresys: CoreSys, capture_message: Mock):
    """Test check does nothing when not running on Home Assistant OS."""
    systemd_unit_failure = CheckSystemdUnitFailure(coresys)

    with patch.object(
        coresys.dbus.systemd,
        "list_units_filtered",
        new_callable=AsyncMock,
        return_value=[("example.service",)],
    ) as list_units_filtered:
        await systemd_unit_failure.run_check()

    list_units_filtered.assert_not_called()
    assert not coresys.resolution.issues
    assert not coresys.resolution.suggestions
    capture_message.assert_not_called()


@pytest.mark.usefixtures("os_available")
@pytest.mark.parametrize(
    ("unit_name", "unhealthy_reason"),
    [
        (
            "systemd-fsck@dev-disk-by\\x2dlabel-hassos\\x2dboot.service",
            UnhealthyReason.OS_FILESYSTEM_CHECK_ERROR,
        ),
        (
            "systemd-fsck@dev-disk-by\\x2dlabel-hassos\\x2doverlay.service",
            UnhealthyReason.OS_FILESYSTEM_CHECK_ERROR,
        ),
        (
            DATA_FSCK_UNIT,
            UnhealthyReason.DATA_FILESYSTEM_CHECK_ERROR,
        ),
    ],
)
async def test_fsck_failures_set_correct_unhealthy_reason(
    coresys: CoreSys,
    capture_message: Mock,
    unit_name: str,
    unhealthy_reason: UnhealthyReason,
):
    """Test fsck failures set expected unhealthy reason."""
    systemd_unit_failure = CheckSystemdUnitFailure(coresys)
    assert unit_name in OS_FSCK_UNITS or unit_name == DATA_FSCK_UNIT

    with patch.object(
        coresys.dbus.systemd,
        "list_units_filtered",
        new_callable=AsyncMock,
        return_value=[(unit_name,)],
    ):
        await systemd_unit_failure.run_check()

    assert unhealthy_reason in coresys.resolution.unhealthy
    assert not coresys.resolution.issues
    assert not coresys.resolution.suggestions
    capture_message.assert_not_called()


async def test_throttled_approve_only_calls_dbus_once_for_multiple_issues(
    coresys: CoreSys,
):
    """Test approve checks reuse throttled cache for multiple issues."""
    systemd_unit_failure = CheckSystemdUnitFailure(coresys)
    await coresys.core.set_state(CoreState.SETUP)

    coresys.resolution.add_issue(
        Issue(IssueType.SYSTEMD_UNIT_FAILED, ContextType.SYSTEM, reference="a.service")
    )
    coresys.resolution.add_issue(
        Issue(IssueType.SYSTEMD_UNIT_FAILED, ContextType.SYSTEM, reference="b.service")
    )

    with patch.object(
        coresys.dbus.systemd,
        "list_units_filtered",
        new_callable=AsyncMock,
        return_value=[("a.service",), ("b.service",)],
    ) as list_units_filtered:
        await systemd_unit_failure()

    assert list_units_filtered.await_count == 1
    assert len(coresys.resolution.issues) == 2


async def test_did_run(coresys: CoreSys):
    """Test that the check runs only in expected states."""
    systemd_unit_failure = CheckSystemdUnitFailure(coresys)
    should_run = systemd_unit_failure.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert should_run == [CoreState.SETUP]
    assert len(should_not_run) != 0

    with patch.object(
        CheckSystemdUnitFailure,
        "run_check",
        return_value=None,
    ) as check:
        for state in should_run:
            await coresys.core.set_state(state)
            await systemd_unit_failure()
            check.assert_called_once()
            check.reset_mock()

        for state in should_not_run:
            await coresys.core.set_state(state)
            await systemd_unit_failure()
            check.assert_not_called()
            check.reset_mock()
