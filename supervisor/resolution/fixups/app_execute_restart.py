"""Helpers to fix app by restarting it."""

import logging

from ...coresys import CoreSys
from ...exceptions import AppsError, ResolutionFixupError
from ..const import ContextType, IssueType, SuggestionType
from .base import FixupBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


def setup(coresys: CoreSys) -> FixupBase:
    """Check setup function."""
    return FixupAppExecuteRestart(coresys)


class FixupAppExecuteRestart(FixupBase):
    """Storage class for fixup."""

    async def process_fixup(self, reference: str | None = None) -> None:
        """Initialize the fixup class."""
        if not reference:
            return

        if not (app := self.sys_apps.get_local_only(reference)):
            _LOGGER.info("Cannot restart app %s as it does not exist", reference)
            return

        # Stop app
        try:
            await app.stop()
        except AppsError as err:
            _LOGGER.error("Could not stop %s due to %s", reference, err)
            raise ResolutionFixupError() from None

        # Start app
        # Removing the container has already fixed the issue and dismissed it
        # So any errors on startup are just logged. We won't wait on the startup task either
        try:
            await app.start()
        except AppsError as err:
            _LOGGER.error("Could not restart %s due to %s", reference, err)

    @property
    def suggestion(self) -> SuggestionType:
        """Return a SuggestionType enum."""
        return SuggestionType.EXECUTE_RESTART

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.ADDON

    @property
    def issues(self) -> list[IssueType]:
        """Return a IssueType enum list."""
        return [IssueType.DEVICE_ACCESS_MISSING]

    @property
    def auto(self) -> bool:
        """Return if a fixup can be apply as auto fix."""
        return False
