"""Helpers to fix app issue by removing it."""

import logging

from ...coresys import CoreSys
from ...exceptions import AppsError, ResolutionFixupError
from ..const import ContextType, IssueType, SuggestionType
from .base import FixupBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


def setup(coresys: CoreSys) -> FixupBase:
    """Check setup function."""
    return FixupAppExecuteRemove(coresys)


class FixupAppExecuteRemove(FixupBase):
    """Storage class for fixup."""

    async def process_fixup(self, reference: str | None = None) -> None:
        """Initialize the fixup class."""
        if not reference:
            return

        if not (app := self.sys_apps.get_local_only(reference)):
            _LOGGER.info("App %s already removed", reference)
            return

        # Remove app
        _LOGGER.info("Remove app: %s", reference)
        try:
            await app.uninstall(remove_config=False)
        except AppsError as err:
            _LOGGER.error("Could not remove %s due to %s", reference, err)
            raise ResolutionFixupError() from None

    @property
    def suggestion(self) -> SuggestionType:
        """Return a SuggestionType enum."""
        return SuggestionType.EXECUTE_REMOVE

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.ADDON

    @property
    def issues(self) -> list[IssueType]:
        """Return a IssueType enum list."""
        return [IssueType.DETACHED_ADDON_REMOVED, IssueType.DEPRECATED_ARCH_ADDON]

    @property
    def auto(self) -> bool:
        """Return if a fixup can be apply as auto fix."""
        return False
