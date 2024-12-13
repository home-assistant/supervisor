"""Helpers to fix addon by starting it."""

import logging

from ...const import AddonState
from ...coresys import CoreSys
from ...exceptions import AddonsError, ResolutionFixupError
from ..const import ContextType, IssueType, SuggestionType
from .base import FixupBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


def setup(coresys: CoreSys) -> FixupBase:
    """Check setup function."""
    return FixupAddonExecuteStart(coresys)


class FixupAddonExecuteStart(FixupBase):
    """Storage class for fixup."""

    async def process_fixup(self, reference: str | None = None) -> None:
        """Initialize the fixup class."""
        if not (addon := self.sys_addons.get(reference, local_only=True)):
            _LOGGER.info("Cannot start addon %s as it does not exist", reference)
            return

        # Start addon
        try:
            start_task = await addon.start()
        except AddonsError as err:
            _LOGGER.error("Could not start %s due to %s", reference, err)
            raise ResolutionFixupError() from None

        # Wait for addon start. If it ends up in error or unknown state it's not fixed
        await start_task
        if addon.state in {AddonState.ERROR, AddonState.UNKNOWN}:
            _LOGGER.error("Addon %s could not start successfully", reference)
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
