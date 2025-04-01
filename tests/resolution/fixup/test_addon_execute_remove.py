"""Test evaluation base."""

from unittest.mock import patch

from supervisor.addons.addon import Addon
from supervisor.coresys import CoreSys
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion
from supervisor.resolution.fixups.addon_execute_remove import FixupAddonExecuteRemove


async def test_fixup(coresys: CoreSys, install_addon_ssh: Addon):
    """Test fixup."""
    addon_execute_remove = FixupAddonExecuteRemove(coresys)

    assert addon_execute_remove.auto is False

    coresys.resolution.add_suggestion(
        Suggestion(
            SuggestionType.EXECUTE_REMOVE,
            ContextType.ADDON,
            reference=install_addon_ssh.slug,
        )
    )
    coresys.resolution.add_issue(
        Issue(
            IssueType.DETACHED_ADDON_REMOVED,
            ContextType.ADDON,
            reference=install_addon_ssh.slug,
        )
    )

    with patch.object(Addon, "uninstall") as uninstall:
        await addon_execute_remove()

        assert uninstall.called

    assert len(coresys.resolution.suggestions) == 0
    assert len(coresys.resolution.issues) == 0
