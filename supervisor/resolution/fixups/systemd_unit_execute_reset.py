"""Fixup to reset failed systemd unit."""

import logging

from ...coresys import CoreSys
from ...exceptions import DBusError, DBusSystemdNoSuchUnit, ResolutionFixupError
from ...resolution.const import ContextType, IssueType, SuggestionType
from ...resolution.data import Suggestion
from .base import FixupBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


def setup(coresys: CoreSys) -> FixupBase:
    """Fixup setup function."""
    return FixupSystemdUnitExecuteReset(coresys)


class FixupSystemdUnitExecuteReset(FixupBase):
    """Fixup to reset failed state of a systemd unit."""

    async def process_fixup(self, suggestion: Suggestion) -> None:
        """Reset the failed state of the unit."""
        if not suggestion.reference:
            _LOGGER.warning("No unit reference provided for systemd reset fixup")
            return

        unit_name = suggestion.reference
        try:
            _LOGGER.info("Resetting failed state of systemd unit: %s", unit_name)
            await self.sys_dbus.systemd.reset_failed_unit(unit_name)
        except DBusSystemdNoSuchUnit:
            _LOGGER.warning("Systemd unit not found: %s", unit_name)
        except DBusError as err:
            _LOGGER.error("Failed to reset systemd unit %s: %s", unit_name, err)
            raise ResolutionFixupError from err

    @property
    def suggestion(self) -> SuggestionType:
        """Return SuggestionType enum."""
        return SuggestionType.EXECUTE_RESET

    @property
    def context(self) -> ContextType:
        """Return ContextType enum."""
        return ContextType.SYSTEM

    @property
    def issues(self) -> list[IssueType]:
        """Return affected IssueType enums."""
        return [IssueType.SYSTEMD_UNIT_FAILED]

    @property
    def auto(self) -> bool:
        """Return if auto fixup is enabled."""
        return False
