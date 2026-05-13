"""Helpers to fix app by starting it."""

import logging

from ...const import AppState
from ...coresys import CoreSys
from ...exceptions import AppsError, ResolutionFixupError
from ..const import ContextType, IssueType, SuggestionType
from .base import FixupBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


def setup(coresys: CoreSys) -> FixupBase:
    """Check setup function."""
    return FixupAppExecuteStart(coresys)


class FixupAppExecuteStart(FixupBase):
    """Storage class for fixup."""

    async def process_fixup(self, reference: str | None = None) -> None:
        """Initialize the fixup class."""
        if not reference:
            return

        if not (app := self.sys_apps.get_local_only(reference)):
            _LOGGER.info("Cannot start app %s as it does not exist", reference)
            return

        # Start app
        try:
            start_task = await app.start()
        except AppsError as err:
            _LOGGER.error("Could not start %s due to %s", reference, err)
            raise ResolutionFixupError() from None

        # Wait for app start. If it ends up in error or unknown state it's not fixed
        await start_task
        if app.state in {AppState.ERROR, AppState.UNKNOWN}:
            _LOGGER.error("App %s could not start successfully", reference)
            raise ResolutionFixupError()

    @property
    def suggestion(self) -> SuggestionType:
        """Return a SuggestionType enum."""
        return SuggestionType.EXECUTE_START

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.ADDON

    @property
    def issues(self) -> list[IssueType]:
        """Return a IssueType enum list."""
        return [IssueType.BOOT_FAIL]

    @property
    def auto(self) -> bool:
        """Return if a fixup can be apply as auto fix."""
        return False
