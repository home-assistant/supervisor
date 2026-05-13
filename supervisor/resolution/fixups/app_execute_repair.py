"""Helper to fix missing image for app."""

import logging

from ...coresys import CoreSys
from ..const import ContextType, IssueType, SuggestionType
from .base import FixupBase

_LOGGER: logging.Logger = logging.getLogger(__name__)
MAX_AUTO_ATTEMPTS = 5


def setup(coresys: CoreSys) -> FixupBase:
    """Check setup function."""
    return FixupAppExecuteRepair(coresys)


class FixupAppExecuteRepair(FixupBase):
    """Storage class for fixup."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize the app execute repair fixup class."""
        super().__init__(coresys)
        self.attempts = 0

    async def process_fixup(self, reference: str | None = None) -> None:
        """Pull the apps image."""
        if not reference:
            return

        app = self.sys_apps.get_local_only(reference)
        if not app:
            _LOGGER.info(
                "Cannot repair app %s as it is not installed, dismissing suggestion",
                reference,
            )
            return

        if await app.instance.exists():
            _LOGGER.info(
                "App %s does not need repair, dismissing suggestion", reference
            )
            return

        _LOGGER.info("Installing image for app %s", reference)
        self.attempts += 1
        await app.instance.install(app.version)

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
