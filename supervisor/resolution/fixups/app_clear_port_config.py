"""Helpers to fix app port conflict with other components."""

import logging
from typing import Any

from ...coresys import CoreSys
from ..const import ContextType, IssueType, SuggestionType
from .base import FixupBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


def setup(coresys: CoreSys) -> FixupBase:
    """Check setup function."""
    return FixupAppClearPortConfig(coresys)


class FixupAppClearPortConfig(FixupBase):
    """Storage class for fixup."""

    async def process_fixup(
        self,
        reference: str | None = None,
        reference_extra: dict[str, Any] | None = None,
    ) -> None:
        """Remove the port mapping that causing a conflict."""
        if not reference or not reference_extra:
            return

        conflict_port = reference_extra.get("port")
        if not isinstance(conflict_port, int):
            return

        app = self.sys_apps.get_local_only(reference)
        if not app:
            _LOGGER.info(
                "Cannot clear port config for app %s as it does not exist", reference
            )
            return

        ports = app.ports
        if not ports:
            _LOGGER.info(
                "App %s has no configurable ports; nothing to clear", reference
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
                reference,
                conflict_port,
            )
            return

        ports[port_key] = None
        await app.save_persist()

        _LOGGER.info(
            "Cleared port %d mapping from app %s to resolve port conflict",
            conflict_port,
            reference,
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
        return [IssueType.APP_PORT_CONFLICT, IssueType.APP_PORT_CONFLICT_CORE]

    @property
    def auto(self) -> bool:
        """Return if a fixup can be apply as auto fix."""
        return False
