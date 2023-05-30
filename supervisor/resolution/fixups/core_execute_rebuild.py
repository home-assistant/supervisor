"""Helper to fix an issue with core by rebuilding its container."""

import logging

from ...coresys import CoreSys
from ...docker.const import ContainerState
from ..const import ContextType, IssueType, SuggestionType
from .base import FixupBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


def setup(coresys: CoreSys) -> FixupBase:
    """Check setup function."""
    return FixupCoreExecuteRebuild(coresys)


class FixupCoreExecuteRebuild(FixupBase):
    """Storage class for fixup."""

    async def process_fixup(self, reference: str | None = None) -> None:
        """Rebuild the core container."""
        state = await self.sys_homeassistant.core.instance.current_state()

        if state == ContainerState.UNKNOWN:
            _LOGGER.info(
                "Container for Home Assistant does not exist, it will be rebuilt when started next"
            )
        elif state == ContainerState.STOPPED:
            _LOGGER.info(
                "Home Assistant is stopped, removing its container so it rebuilds when started next"
            )
            await self.sys_homeassistant.core.instance.stop()
        else:
            await self.sys_homeassistant.core.rebuild()

    @property
    def suggestion(self) -> SuggestionType:
        """Return a SuggestionType enum."""
        return SuggestionType.EXECUTE_REBUILD

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.CORE

    @property
    def issues(self) -> list[IssueType]:
        """Return a IssueType enum list."""
        return [IssueType.DOCKER_CONFIG]
