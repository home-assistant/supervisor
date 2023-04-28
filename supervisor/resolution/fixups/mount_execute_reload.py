"""Helper to fix an issue with a mount by retrying it."""

import logging

from ...coresys import CoreSys
from ...exceptions import MountNotFound
from ..const import ContextType, IssueType, SuggestionType
from .base import FixupBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


def setup(coresys: CoreSys) -> FixupBase:
    """Check setup function."""
    return FixupMountExecuteReload(coresys)


class FixupMountExecuteReload(FixupBase):
    """Storage class for fixup."""

    async def process_fixup(self, reference: str | None = None) -> None:
        """Attempt to remount using the same config to fix failure."""
        try:
            await self.sys_mounts.reload_mount(reference)
        except MountNotFound:
            _LOGGER.warning("Can't find mount %s for fixup", reference)

    @property
    def suggestion(self) -> SuggestionType:
        """Return a SuggestionType enum."""
        return SuggestionType.EXECUTE_RELOAD

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
