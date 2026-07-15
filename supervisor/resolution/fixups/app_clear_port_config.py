"""Helpers to fix app port conflict with other components."""

import logging

from ...coresys import CoreSys
from ..const import ContextType, IssueType, SuggestionType
from ..data import Suggestion
from .base import FixupBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


def setup(coresys: CoreSys) -> FixupBase:
    """Check setup function."""
    return FixupAppClearPortConfig(coresys)


class FixupAppClearPortConfig(FixupBase):
    """Storage class for fixup."""

    async def process_fixup(self, suggestion: Suggestion) -> None:
        """Remove the port mapping that causing a conflict."""
        if not suggestion.reference or not suggestion.reference_extra:
            return

        conflict_port = suggestion.reference_extra.get("port")
        if not isinstance(conflict_port, int):
            return

        app = self.sys_apps.get_local_only(suggestion.reference)
        if not app:
            _LOGGER.info(
                "Cannot clear port config for app %s as it does not exist",
                suggestion.reference,
            )
            return

        ports = app.ports
        if not ports:
            _LOGGER.info(
                "App %s has no configurable ports; nothing to clear",
                suggestion.reference,
            )
            return

        port_key: str | None = None
        for def_port, host_port in ports.items():
            if host_port == conflict_port:
                port_key = def_port
                break

        if port_key is None:
            _LOGGER.info(
                "App %s does not map port %d; nothing to clear",
                suggestion.reference,
                conflict_port,
            )
            return

        # Persist only the cleared port as a user override on top of any
        # existing ones, so clearing one conflicting port doesn't turn the
        # current config defaults into user changes.
        app.ports = {**app.user_ports(), port_key: None}
        await app.save_persist()

        _LOGGER.info(
            "Cleared port %d mapping from app %s to resolve port conflict",
            conflict_port,
            suggestion.reference,
        )

    @property
    def suggestion(self) -> SuggestionType:
        """Return a SuggestionType enum."""
        return SuggestionType.CLEAR_PORT_CONFIG

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.ADDON

    @property
    def issues(self) -> list[IssueType]:
        """Return a IssueType enum list."""
        return [IssueType.APP_PORT_CONFLICT]

    @property
    def auto(self) -> bool:
        """Return if a fixup can be apply as auto fix."""
        return False
