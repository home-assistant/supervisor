"""Helpers to clear reboot required issues once the host rebooted."""

import logging

from ...const import CoreState
from ...coresys import CoreSys
from ..const import ContextType, IssueType
from ..data import Issue
from .base import CheckBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


def setup(coresys: CoreSys) -> CheckBase:
    """Check setup function."""
    return CheckRebootRequired(coresys)


class CheckRebootRequired(CheckBase):
    """CheckRebootRequired class for check."""

    async def run_check(self) -> None:
        """Run check if not affected by issue.

        A pending reboot is only known from the operation that requires it,
        so the issue is raised by that operation and not detected here.
        """

    async def approve_check(self, issue: Issue) -> bool:
        """Approve check if it is affected by issue.

        The host cannot reboot while Supervisor keeps running, so a reboot
        only shows up on Supervisor startup: the stored last boot time is
        from the previous Supervisor run and is only updated once startup
        completes.
        """
        if not (last_boot := await self.sys_hardware.helper.last_boot()):
            _LOGGER.warning("Can't determine last boot time, keeping issue")
            return True
        return last_boot == self.sys_config.last_boot

    @property
    def issue(self) -> IssueType:
        """Return a IssueType enum."""
        return IssueType.REBOOT_REQUIRED

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.SYSTEM

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this check can run."""
        return [CoreState.SETUP]
