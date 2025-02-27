"""Helper to fix an issue with a mount by removing it."""

import logging

from ...coresys import CoreSys
from ...exceptions import MountNotFound
from ..const import ContextType, IssueType, SuggestionType
from .base import FixupBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


def setup(coresys: CoreSys) -> FixupBase:
    """Check setup function."""
    return FixupMountExecuteRemove(coresys)


class FixupMountExecuteRemove(FixupBase):
    """Storage class for fixup."""

    async def process_fixup(self, reference: str | None = None) -> None:
        """Remove the failed mount."""
        try:
            await self.sys_mounts.remove_mount(reference)
        except MountNotFound:
            _LOGGER.warning("Can't find mount %s for fixup", reference)
        else:
            await self.sys_mounts.save_data()

    @property
    def suggestion(self) -> SuggestionType:
        """Return a SuggestionType enum."""
        return SuggestionType.EXECUTE_REMOVE

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.MOUNT

    @property
    def issues(self) -> list[IssueType]:
        """Return a IssueType enum list."""
        return [IssueType.MOUNT_FAILED]

    @property
    def auto(self) -> bool:
        """Return if a fixup can be apply as auto fix."""
        return False
