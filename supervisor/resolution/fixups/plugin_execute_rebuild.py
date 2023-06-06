"""Helper to fix an issue with an plugin by rebuilding its container."""

from ...coresys import CoreSys
from ..const import ContextType, IssueType, SuggestionType
from .base import FixupBase


def setup(coresys: CoreSys) -> FixupBase:
    """Check setup function."""
    return FixupPluginExecuteRebuild(coresys)


class FixupPluginExecuteRebuild(FixupBase):
    """Storage class for fixup."""

    async def process_fixup(self, reference: str | None = None) -> None:
        """Rebuild the plugin's container."""
        plugin = next(
            (
                plugin
                for plugin in self.sys_plugins.all_plugins
                if plugin.slug == reference
            ),
            None,
        )
        if not plugin:
            return

        await plugin.rebuild()

    @property
    def suggestion(self) -> SuggestionType:
        """Return a SuggestionType enum."""
        return SuggestionType.EXECUTE_REBUILD

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.PLUGIN

    @property
    def issues(self) -> list[IssueType]:
        """Return a IssueType enum list."""
        return [IssueType.DOCKER_CONFIG]

    @property
    def auto(self) -> bool:
        """Return if a fixup can be apply as auto fix."""
        return True
