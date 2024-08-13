"""Test fixup system execute rebuild."""

from unittest.mock import patch

from supervisor.coresys import CoreSys
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.fixups.addon_execute_rebuild import FixupAddonExecuteRebuild
from supervisor.resolution.fixups.core_execute_rebuild import FixupCoreExecuteRebuild
from supervisor.resolution.fixups.plugin_execute_rebuild import (
    FixupPluginExecuteRebuild,
)
from supervisor.resolution.fixups.system_execute_rebuild import (
    FixupSystemExecuteRebuild,
)


async def test_fixup(coresys: CoreSys):
    """Test fixup applies other rebuild fixups for docker config issues."""
    system_execute_rebuild = FixupSystemExecuteRebuild(coresys)

    assert system_execute_rebuild.auto is False

    coresys.resolution.create_issue(
        IssueType.DOCKER_CONFIG,
        ContextType.ADDON,
        reference="local_ssh",
        suggestions=[SuggestionType.EXECUTE_REBUILD],
    )
    coresys.resolution.create_issue(
        IssueType.DOCKER_CONFIG,
        ContextType.CORE,
        suggestions=[SuggestionType.EXECUTE_REBUILD],
    )
    coresys.resolution.create_issue(
        IssueType.DOCKER_CONFIG,
        ContextType.PLUGIN,
        reference="audio",
        suggestions=[SuggestionType.EXECUTE_REBUILD],
    )
    coresys.resolution.create_issue(
        IssueType.DOCKER_CONFIG,
        ContextType.SYSTEM,
        suggestions=[SuggestionType.EXECUTE_REBUILD],
    )
    with (
        patch.object(FixupAddonExecuteRebuild, "process_fixup") as addon_fixup,
        patch.object(FixupCoreExecuteRebuild, "process_fixup") as core_fixup,
        patch.object(FixupPluginExecuteRebuild, "process_fixup") as plugin_fixup,
    ):
        await system_execute_rebuild()
        addon_fixup.assert_called_once_with(reference="local_ssh")
        core_fixup.assert_called_once()
        plugin_fixup.assert_called_once_with(reference="audio")

    assert not coresys.resolution.issues
    assert not coresys.resolution.suggestions
