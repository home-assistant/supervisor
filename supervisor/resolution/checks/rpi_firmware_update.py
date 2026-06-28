"""Check for Raspberry Pi firmware updates."""

from ...const import CoreState
from ...coresys import CoreSys
from ...os.const import RPI_FIRMWARE_MIN_OS_AGENT_VERSION
from ..const import ContextType, IssueType
from ..data import Issue
from ..utils import sync_rpi_firmware_issues
from .base import CheckBase


def setup(coresys: CoreSys) -> CheckBase:
    """Check setup function."""
    return CheckRpiFirmwareUpdate(coresys)


class CheckRpiFirmwareUpdate(CheckBase):
    """Check for Raspberry Pi firmware updates."""

    async def __call__(self) -> None:
        """Execute the check."""
        if self.sys_core.state not in self.states:
            return

        await self.run_check()

    def _has_rpi_firmware_management(self) -> bool:
        """Return true if Raspberry Pi firmware management is available."""
        return (
            self.sys_dbus.agent.is_connected
            and self.sys_dbus.agent.version >= RPI_FIRMWARE_MIN_OS_AGENT_VERSION
            and self.sys_dbus.agent.board.has_rpi_firmware
        )

    async def run_check(self) -> None:
        """Run check if not affected by issue."""
        if not self._has_rpi_firmware_management():
            return

        sync_rpi_firmware_issues(self.coresys, self.sys_dbus.agent.board.rpi_firmware)

    async def approve_check(self, issue: Issue) -> bool:
        """Approve check if it is affected by issue."""
        if not self._has_rpi_firmware_management():
            return False

        rpi = self.sys_dbus.agent.board.rpi_firmware
        return (
            rpi.update_available and not rpi.update_blocked and not rpi.update_pending
        )

    @property
    def issue(self) -> IssueType:
        """Return a IssueType enum."""
        return IssueType.RPI_FIRMWARE_UPDATE_AVAILABLE

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.SYSTEM

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this check can run."""
        return [CoreState.RUNNING, CoreState.STARTUP]
