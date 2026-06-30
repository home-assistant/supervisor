"""Check for failed systemd units."""

import asyncio
from collections.abc import Awaitable
from datetime import timedelta
import logging

from ...const import CoreState
from ...coresys import CoreSys
from ...host.firewall import FIREWALL_SERVICE
from ...jobs.const import JobThrottle
from ...jobs.decorator import Job
from ...utils.sentry import async_capture_message
from ..const import ContextType, IssueType, SuggestionType, UnhealthyReason
from ..data import Issue
from .base import CheckBase

_LOGGER: logging.Logger = logging.getLogger(__name__)

# Systemd fsck units for OS boot and overlay
OS_FSCK_UNITS = {
    "systemd-fsck@dev-disk-by\\x2dlabel-hassos\\x2dboot.service",
    "systemd-fsck@dev-disk-by\\x2dlabel-hassos\\x2doverlay.service",
}

# Systemd fsck unit for data filesystem
DATA_FSCK_UNIT = "systemd-fsck@dev-disk-by\\x2dlabel-hassos\\x2ddata.service"


def setup(coresys: CoreSys) -> CheckBase:
    """Check setup function."""
    return CheckSystemdUnitFailure(coresys)


class CheckSystemdUnitFailure(CheckBase):
    """Check for failed systemd units and create repair suggestions."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize systemd unit failure check."""
        super().__init__(coresys)
        self._failed_units_cache: list[tuple[str, ...]] = []

    @Job(
        name="resolution_check_systemd_unit_failure_list_units_filtered",
        throttle=JobThrottle.THROTTLE,
        throttle_period=timedelta(seconds=60),
        internal=True,
    )
    async def _refresh_failed_units_cache(self) -> None:
        """Refresh cached failed units at most once per throttle period."""
        self._failed_units_cache = await self.sys_dbus.systemd.list_units_filtered(
            ["failed"]
        )

    async def _get_failed_units(self) -> list[tuple[str, ...]]:
        """Return failed units using a throttled cached fetch."""
        await self._refresh_failed_units_cache()
        return self._failed_units_cache

    async def run_check(self) -> None:
        """Run check to list failed systemd units."""
        # Get all failed units
        failed_units = await self._get_failed_units()
        capture_coroutines: list[Awaitable[None]] = []

        if not failed_units:
            return

        # Get managed mount unit names from mounts and bound_mounts
        managed_mounts = set()
        for mount in self.sys_mounts.mounts:
            managed_mounts.add(mount.unit_name)
        for bound_mount in self.sys_mounts.bound_mounts:
            managed_mounts.add(bound_mount.mount.unit_name)

        for unit in failed_units:
            unit_name = unit[0]

            # Skip mount units managed by MountManager
            if unit_name in managed_mounts:
                _LOGGER.debug(
                    "Ignoring failed mount unit '%s' managed by MountManager",
                    unit_name,
                )
                continue

            # Skip firewall service which handles its own health state
            if unit_name == FIREWALL_SERVICE:
                _LOGGER.debug(
                    "Ignoring failed firewall service '%s' which handles its own health state",
                    unit_name,
                )
                continue

            # Check for OS fsck failures
            if unit_name in OS_FSCK_UNITS:
                _LOGGER.error("OS filesystem check failed: %s", unit_name)
                self.sys_resolution.add_unhealthy_reason(
                    UnhealthyReason.OS_FILESYSTEM_CHECK_ERROR
                )
                continue

            # Check for data fsck failure
            if unit_name == DATA_FSCK_UNIT:
                _LOGGER.error("Data filesystem check failed: %s", unit_name)
                self.sys_resolution.add_unhealthy_reason(
                    UnhealthyReason.DATA_FILESYSTEM_CHECK_ERROR
                )
                continue

            # Create issue for other failed units
            issue = Issue(
                IssueType.SYSTEMD_UNIT_FAILED, ContextType.SYSTEM, reference=unit_name
            )
            if issue in self.sys_resolution.issues:
                continue

            capture_coroutines.append(
                async_capture_message(
                    f"Systemd unit failed: {unit_name}",
                    level="error",
                )
            )
            self.sys_resolution.add_issue(
                issue,
                suggestions=[
                    SuggestionType.EXECUTE_RESET,
                    SuggestionType.EXECUTE_RESTART,
                ],
            )

        if capture_coroutines:
            await asyncio.gather(*capture_coroutines)

    async def approve_check(self, issue: Issue) -> bool:
        """Approve check if it is affected by issue."""
        if not issue.reference:
            return False

        # Check if the failed unit still exists in failed units
        failed_units = await self._get_failed_units()
        return any(unit[0] == issue.reference for unit in failed_units)

    @property
    def issue(self) -> IssueType:
        """Return an IssueType enum."""
        return IssueType.SYSTEMD_UNIT_FAILED

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.SYSTEM

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this check can run."""
        return [CoreState.SETUP]
