"""Helpers to fix addon by restarting it."""

import logging

from ...coresys import CoreSys
from ...exceptions import AddonsError, ResolutionFixupError
from ..const import ContextType, IssueType, SuggestionType
from .base import FixupBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


def setup(coresys: CoreSys) -> FixupBase:
    """Check setup function."""
    return FixupAddonExecuteRestart(coresys)


class FixupAddonExecuteRestart(FixupBase):
    """Storage class for fixup."""

    async def process_fixup(self, reference: str | None = None) -> None:
        """Initialize the fixup class."""
        if not (addon := self.sys_addons.get(reference, local_only=True)):
            _LOGGER.info("Cannot restart addon %s as it does not exist", reference)
            return

        # Stop addon
        try:
            await addon.stop()
        except AddonsError as err:
            _LOGGER.error("Could not stop %s due to %s", reference, err)
            raise ResolutionFixupError() from None

        # Start addon
        # Removing the container has already fixed the issue and dismissed it
        # So any errors on startup are just logged. We won't wait on the startup task either
        try:
            await addon.start()
        except AddonsError as err:
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
