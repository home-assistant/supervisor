"""Helpers to check disk lifetime issues."""

from ...const import CoreState
from ...coresys import CoreSys
from ..const import ContextType, IssueType
from .base import CheckBase


def setup(coresys: CoreSys) -> CheckBase:
    """Check setup function."""
    return CheckDiskLifetime(coresys)


class CheckDiskLifetime(CheckBase):
    """Storage class for check."""

    async def run_check(self) -> None:
        """Run check if not affected by issue."""
        if await self.approve_check():
            self.sys_resolution.create_issue(
                IssueType.DISK_LIFETIME, ContextType.SYSTEM
            )

    async def approve_check(self, reference: str | None = None) -> bool:
        """Approve check if it is affected by issue."""
        # Get the current data disk device
        if not self.sys_dbus.agent.datadisk.current_device:
            return False

        # Check disk lifetime
        lifetime = await self.sys_hardware.disk.get_disk_life_time(
            self.sys_dbus.agent.datadisk.current_device
        )

        # Issue still exists if lifetime is >= 90%
        return lifetime is not None and lifetime >= 90

    @property
    def issue(self) -> IssueType:
        """Return a IssueType enum."""
        return IssueType.DISK_LIFETIME

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.SYSTEM

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this check can run."""
        return [CoreState.RUNNING, CoreState.STARTUP]
