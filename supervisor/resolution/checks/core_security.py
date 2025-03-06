"""Helpers to check core security."""

from enum import StrEnum
from pathlib import Path

from awesomeversion import AwesomeVersion, AwesomeVersionException

from ...const import CoreState
from ...coresys import CoreSys
from ..const import ContextType, IssueType, SuggestionType
from .base import CheckBase


def setup(coresys: CoreSys) -> CheckBase:
    """Check setup function."""
    return CheckCoreSecurity(coresys)


class SecurityReference(StrEnum):
    """Version references."""

    CUSTOM_COMPONENTS_BELOW_2021_1_5 = "custom_components_below_2021_1_5"


class CheckCoreSecurity(CheckBase):
    """CheckCoreSecurity class for check."""

    async def run_check(self) -> None:
        """Run check if not affected by issue."""
        # Security issue < 2021.1.5 & Custom components
        try:
            if self.sys_homeassistant.version < AwesomeVersion("2021.1.5"):
                if await self.sys_run_in_executor(self._custom_components_exists):
                    self.sys_resolution.create_issue(
                        IssueType.SECURITY,
                        ContextType.CORE,
                        reference=SecurityReference.CUSTOM_COMPONENTS_BELOW_2021_1_5,
                        suggestions=[SuggestionType.EXECUTE_UPDATE],
                    )
        except (AwesomeVersionException, OSError):
            return

    async def approve_check(self, reference: str | None = None) -> bool:
        """Approve check if it is affected by issue."""
        try:
            if self.sys_homeassistant.version >= AwesomeVersion("2021.1.5"):
                return False
        except AwesomeVersionException:
            return True
        return await self.sys_run_in_executor(self._custom_components_exists)

    def _custom_components_exists(self) -> bool:
        """Return true if custom components folder exists.

        Must be run in executor.
        """
        return Path(self.sys_config.path_homeassistant, "custom_components").exists()

    @property
    def issue(self) -> IssueType:
        """Return a IssueType enum."""
        return IssueType.SECURITY

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.CORE

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this check can run."""
        return [CoreState.RUNNING, CoreState.STARTUP]
