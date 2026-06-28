"""Update Raspberry Pi firmware fixup."""

import asyncio
import logging

from ...coresys import CoreSys
from ..const import ContextType, IssueType, SuggestionType
from ..data import Suggestion
from .base import FixupBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


def setup(coresys: CoreSys) -> FixupBase:
    """Check setup function."""
    return FixupSystemUpdateRpiFirmware(coresys)


class FixupSystemUpdateRpiFirmware(FixupBase):
    """Storage class for fixup."""

    async def process_fixup(self, suggestion: Suggestion) -> None:
        """Update Raspberry Pi firmware."""
        _LOGGER.info("Updating Raspberry Pi firmware")
        await asyncio.shield(self.sys_os.update_raspberrypi_firmware())

    @property
    def suggestion(self) -> SuggestionType:
        """Return a SuggestionType enum."""
        return SuggestionType.UPDATE_RPI_FIRMWARE

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.SYSTEM

    @property
    def issues(self) -> list[IssueType]:
        """Return a IssueType enum list."""
        return [IssueType.RPI_FIRMWARE_UPDATE_AVAILABLE]
