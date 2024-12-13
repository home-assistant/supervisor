"""Helpers to fix addon by disabling boot."""

import logging

from ...const import AddonBoot
from ...coresys import CoreSys
from ..const import ContextType, IssueType, SuggestionType
from .base import FixupBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


def setup(coresys: CoreSys) -> FixupBase:
    """Check setup function."""
    return FixupAddonDisableBoot(coresys)


class FixupAddonDisableBoot(FixupBase):
    """Storage class for fixup."""

    async def process_fixup(self, reference: str | None = None) -> None:
        """Initialize the fixup class."""
        if not (addon := self.sys_addons.get(reference, local_only=True)):
            _LOGGER.info("Cannot change addon %s as it does not exist", reference)
            return

        # Disable boot on addon
        addon.boot = AddonBoot.MANUAL

    @property
    def suggestion(self) -> SuggestionType:
        """Return a SuggestionType enum."""
        return SuggestionType.DISABLE_BOOT

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
