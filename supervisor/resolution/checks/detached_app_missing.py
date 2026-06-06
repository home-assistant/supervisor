"""Helpers to check for detached apps due to repo missing."""

from typing import Any

from ...const import CoreState
from ...coresys import CoreSys
from ..const import ContextType, IssueType
from .base import CheckBase


def setup(coresys: CoreSys) -> CheckBase:
    """Check setup function."""
    return CheckDetachedAppMissing(coresys)


class CheckDetachedAppMissing(CheckBase):
    """CheckDetachedAppMissing class for check."""

    @property
    def slug(self) -> str:
        """Return the check slug."""
        return "detached_addon_missing"

    async def run_check(self) -> None:
        """Run check if not affected by issue."""
        for app in self.sys_apps.installed:
            if app.is_detached and app.repository not in self.sys_store.repositories:
                self.sys_resolution.create_issue(
                    IssueType.DETACHED_ADDON_MISSING,
                    ContextType.ADDON,
                    reference=app.slug,
                )

    async def approve_check(
        self,
        reference: str | None = None,
        reference_extra: dict[str, Any] | None = None,
    ) -> bool:
        """Approve check if it is affected by issue."""
        if not reference:
            return False

        app = self.sys_apps.get_local_only(reference)
        return app is not None and app.is_detached

    @property
    def issue(self) -> IssueType:
        """Return a IssueType enum."""
        return IssueType.DETACHED_ADDON_MISSING

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.ADDON

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this check can run."""
        return [CoreState.SETUP]
