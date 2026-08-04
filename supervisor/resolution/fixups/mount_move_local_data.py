"""Helper to fix an issue with a mount by moving local data out of its target."""

import logging

from ...coresys import CoreSys
from ...exceptions import MountError, MountNotFound, ResolutionFixupError
from ..const import ContextType, IssueType, SuggestionType
from ..data import Suggestion
from .base import FixupBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


def setup(coresys: CoreSys) -> FixupBase:
    """Check setup function."""
    return FixupMountMoveLocalData(coresys)


class FixupMountMoveLocalData(FixupBase):
    """Storage class for fixup."""

    async def process_fixup(self, suggestion: Suggestion) -> None:
        """Move local data out of the mount target directories and remount."""
        try:
            await self.sys_mounts.relocate_local_data(suggestion.reference)
        except MountNotFound:
            _LOGGER.warning("Can't find mount %s for fixup", suggestion.reference)
        except MountError as err:
            # Leave the issue/suggestion in place so the user can try again
            _LOGGER.warning(
                "Could not move local data for mount %s: %s", suggestion.reference, err
            )
            raise ResolutionFixupError from err

    @property
    def suggestion(self) -> SuggestionType:
        """Return a SuggestionType enum."""
        return SuggestionType.MOVE_LOCAL_DATA

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.MOUNT

    @property
    def issues(self) -> list[IssueType]:
        """Return a IssueType enum list."""
        return [IssueType.MOUNT_TARGET_NOT_EMPTY]

    @property
    def auto(self) -> bool:
        """Return if a fixup can be apply as auto fix."""
        return False
