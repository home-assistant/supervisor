"""Fixup to restart failed systemd unit."""

import logging

from ...coresys import CoreSys
from ...dbus.const import StartUnitMode
from ...exceptions import DBusError, DBusSystemdNoSuchUnit, ResolutionFixupError
from ...resolution.const import ContextType, IssueType, SuggestionType
from ...resolution.data import Suggestion
from .base import FixupBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


def setup(coresys: CoreSys) -> FixupBase:
    """Fixup setup function."""
    return FixupSystemdUnitExecuteRestart(coresys)


class FixupSystemdUnitExecuteRestart(FixupBase):
    """Fixup to restart a failed systemd unit."""

    async def process_fixup(self, suggestion: Suggestion) -> None:
        """Restart the unit."""
        if not suggestion.reference:
            _LOGGER.warning("No unit reference provided for systemd restart fixup")
            return

        unit_name = suggestion.reference
        try:
            _LOGGER.info("Restarting systemd unit: %s", unit_name)
            await self.sys_dbus.systemd.restart_unit(unit_name, StartUnitMode.REPLACE)
        except DBusSystemdNoSuchUnit:
            _LOGGER.warning("Systemd unit not found: %s", unit_name)
        except DBusError as err:
            _LOGGER.error("Failed to restart systemd unit %s: %s", unit_name, err)
            raise ResolutionFixupError from err

    @property
    def suggestion(self) -> SuggestionType:
        """Return SuggestionType enum."""
        return SuggestionType.EXECUTE_RESTART

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
