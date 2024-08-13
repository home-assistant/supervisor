"""Helpers to fix addon issue by removing it."""

import logging

from ...coresys import CoreSys
from ...exceptions import AddonsError, ResolutionFixupError
from ..const import ContextType, IssueType, SuggestionType
from .base import FixupBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


def setup(coresys: CoreSys) -> FixupBase:
    """Check setup function."""
    return FixupAddonExecuteRemove(coresys)


class FixupAddonExecuteRemove(FixupBase):
    """Storage class for fixup."""

    async def process_fixup(self, reference: str | None = None) -> None:
        """Initialize the fixup class."""
        if not (addon := self.sys_addons.get(reference, local_only=True)):
            _LOGGER.info("Addon %s already removed", reference)
            return

        # Remove addon
        _LOGGER.info("Remove addon: %s", reference)
        try:
            await addon.uninstall(remove_config=False)
        except AddonsError as err:
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
        return [IssueType.DETACHED_ADDON_REMOVED]

    @property
    def auto(self) -> bool:
        """Return if a fixup can be apply as auto fix."""
        return False
