"""Helpers to check core version."""
from enum import Enum
from pathlib import Path
from typing import List

from ...const import SUPERVISOR_DATA, CoreState
from ..const import ContextType, IssueType
from .base import CheckBase

CC_PATH = Path(SUPERVISOR_DATA, "homeassistant", "custom_components")


class VersionReference(str, Enum):
    """Version references."""

    CUSTOM_COMPONENTS_BELOW_2021_1_3 = "custom_components_below_2021_1_3"


class CheckCoreVersion(CheckBase):
    """CheckCoreVersion class for check."""

    async def run_check(self) -> None:
        """Run check if not affected by issue."""
        if not self.sys_homeassistant.version:
            # Can't determine version.
            return

        if self.sys_homeassistant.version < "2021.1.3":
            if CC_PATH.exists():
                self.sys_resolution.create_issue(
                    IssueType.VERSION,
                    ContextType.CORE,
                    reference=VersionReference.CUSTOM_COMPONENTS_BELOW_2021_1_3,
                )

    async def approve_check(self) -> bool:
        """Approve check if it is affected by issue."""
        if not self.sys_homeassistant.version:
            return True
        if self.sys_homeassistant.version >= "2021.1.3":
            return False
        if not CC_PATH.exists():
            return False
        return True

    @property
    def issue(self) -> IssueType:
        """Return a IssueType enum."""
        return IssueType.VERSION

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.CORE

    @property
    def states(self) -> List[CoreState]:
        """Return a list of valid states when this check can run."""
        return [CoreState.RUNNING, CoreState.STARTUP]
