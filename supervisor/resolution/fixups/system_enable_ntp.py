"""Enable NTP fixup."""

import logging

from ...coresys import CoreSys
from ...dbus.const import StartUnitMode
from ..const import ContextType, IssueType, SuggestionType
from .base import FixupBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


def setup(coresys: CoreSys) -> FixupBase:
    """Check setup function."""
    return FixupSystemEnableNTP(coresys)


class FixupSystemEnableNTP(FixupBase):
    """Storage class for fixup."""

    async def process_fixup(self, reference: str | None = None) -> None:
        """Initialize the fixup class."""
        _LOGGER.info("Starting systemd-timesyncd service")
        await self.sys_dbus.systemd.start_unit(
            "systemd-timesyncd.service", StartUnitMode.REPLACE
        )

    @property
    def suggestion(self) -> SuggestionType:
        """Return a SuggestionType enum."""
        return SuggestionType.ENABLE_NTP

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.SYSTEM

    @property
    def issues(self) -> list[IssueType]:
        """Return a IssueType enum list."""
        return [IssueType.NTP_SYNC_FAILED]
