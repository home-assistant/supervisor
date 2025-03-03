"""Helper to fix missing image for addon."""

import logging

from ...coresys import CoreSys
from ..const import ContextType, IssueType, SuggestionType
from .base import FixupBase

_LOGGER: logging.Logger = logging.getLogger(__name__)
MAX_AUTO_ATTEMPTS = 5


def setup(coresys: CoreSys) -> FixupBase:
    """Check setup function."""
    return FixupAddonExecuteRepair(coresys)


class FixupAddonExecuteRepair(FixupBase):
    """Storage class for fixup."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize the add-on execute repair fixup class."""
        super().__init__(coresys)
        self.attempts = 0

    async def process_fixup(self, reference: str | None = None) -> None:
        """Pull the addons image."""
        addon = self.sys_addons.get(reference, local_only=True)
        if not addon:
            _LOGGER.info(
                "Cannot repair addon %s as it is not installed, dismissing suggestion",
                reference,
            )
            return

        if await addon.instance.exists():
            _LOGGER.info(
                "Addon %s does not need repair, dismissing suggestion", reference
            )
            return

        _LOGGER.info("Installing image for addon %s", reference)
        self.attempts += 1
        await addon.instance.install(addon.version)

    @property
    def suggestion(self) -> SuggestionType:
        """Return a SuggestionType enum."""
        return SuggestionType.EXECUTE_REPAIR

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.ADDON

    @property
    def issues(self) -> list[IssueType]:
        """Return a IssueType enum list."""
        return [IssueType.MISSING_IMAGE]

    @property
    def auto(self) -> bool:
        """Return if a fixup can be apply as auto fix."""
        return self.attempts < MAX_AUTO_ATTEMPTS
