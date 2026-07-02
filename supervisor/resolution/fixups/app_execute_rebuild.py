"""Helper to fix an issue with an app by rebuilding its container."""

import logging

from ...coresys import CoreSys
from ...docker.const import ContainerState
from ..const import ContextType, IssueType, SuggestionType
from ..data import Suggestion
from .base import FixupBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


def setup(coresys: CoreSys) -> FixupBase:
    """Check setup function."""
    return FixupAppExecuteRebuild(coresys)


class FixupAppExecuteRebuild(FixupBase):
    """Storage class for fixup."""

    async def process_fixup(self, suggestion: Suggestion) -> None:
        """Rebuild the app's container."""
        if not suggestion.reference:
            return

        app = self.sys_apps.get_local_only(suggestion.reference)
        if not app:
            _LOGGER.info(
                "Cannot rebuild app %s as it is not installed, dismissing suggestion",
                suggestion.reference,
            )
            return

        state = await app.instance.current_state()
        if state == ContainerState.UNKNOWN:
            _LOGGER.info(
                "Container for app %s does not exist, it will be rebuilt when started next",
                suggestion.reference,
            )
        elif state == ContainerState.STOPPED:
            _LOGGER.info(
                "App %s is stopped, removing its container so it rebuilds when started next",
                suggestion.reference,
            )
            await app.stop()
        else:
            await (await app.restart())

    @property
    def suggestion(self) -> SuggestionType:
        """Return a SuggestionType enum."""
        return SuggestionType.EXECUTE_REBUILD

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.ADDON

    @property
    def issues(self) -> list[IssueType]:
        """Return a IssueType enum list."""
        return [IssueType.DOCKER_CONFIG]
