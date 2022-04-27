"""Helpers to check plugin trust."""
import logging
from typing import Optional

from ...const import CoreState
from ...coresys import CoreSys
from ...exceptions import CodeNotaryError, CodeNotaryUntrusted
from ..const import ContextType, IssueType, UnhealthyReason
from .base import CheckBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


def setup(coresys: CoreSys) -> CheckBase:
    """Check setup function."""
    return CheckPluginTrust(coresys)


class CheckPluginTrust(CheckBase):
    """CheckPluginTrust class for check."""

    async def run_check(self) -> None:
        """Run check if not affected by issue."""
        if not self.sys_security.content_trust:
            _LOGGER.warning(
                "Skipping %s, content_trust is globally disabled", self.slug
            )
            return

        for plugin in self.sys_plugins.all_plugins:
            try:
                await plugin.check_trust()
            except CodeNotaryUntrusted:
                self.sys_resolution.unhealthy = UnhealthyReason.UNTRUSTED
                self.sys_resolution.create_issue(
                    IssueType.TRUST, ContextType.PLUGIN, reference=plugin.slug
                )
            except CodeNotaryError:
                pass

    async def approve_check(self, reference: Optional[str] = None) -> bool:
        """Approve check if it is affected by issue."""
        for plugin in self.sys_plugins.all_plugins:
            if reference != plugin.slug:
                continue
            try:
                await plugin.check_trust()
            except CodeNotaryError:
                return True
            return False

    @property
    def issue(self) -> IssueType:
        """Return a IssueType enum."""
        return IssueType.TRUST

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.PLUGIN

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this check can run."""
        return [CoreState.RUNNING, CoreState.STARTUP]
