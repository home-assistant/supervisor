"""Helpers to check if backed up."""

from ...backups.const import BackupType
from ...const import CoreState
from ...coresys import CoreSys
from ..const import ContextType, IssueType, SuggestionType
from .base import CheckBase


def setup(coresys: CoreSys) -> CheckBase:
    """Check setup function."""
    return CheckBackups(coresys)


class CheckBackups(CheckBase):
    """CheckBackups class for check."""

    async def run_check(self) -> None:
        """Run check if not affected by issue."""
        if await self.approve_check():
            self.sys_resolution.create_issue(
                IssueType.NO_CURRENT_BACKUP,
                ContextType.SYSTEM,
                suggestions=[SuggestionType.CREATE_FULL_BACKUP],
            )

    async def approve_check(self, reference: str | None = None) -> bool:
        """Approve check if it is affected by issue."""
        return (
            len(
                [
                    backup
                    for backup in self.sys_backups.list_backups
                    if backup.sys_type == BackupType.FULL and backup.is_current
                ]
            )
            == 0
        )

    @property
    def issue(self) -> IssueType:
        """Return a IssueType enum."""
        return IssueType.NO_CURRENT_BACKUP

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.SYSTEM

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this check can run."""
        return [CoreState.RUNNING, CoreState.STARTUP]
