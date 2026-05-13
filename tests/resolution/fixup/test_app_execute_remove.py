"""Test evaluation base."""

from unittest.mock import patch

from supervisor.apps.app import App
from supervisor.coresys import CoreSys
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion
from supervisor.resolution.fixups.app_execute_remove import FixupAppExecuteRemove


async def test_fixup(coresys: CoreSys, install_app_ssh: App):
    """Test fixup."""
    app_execute_remove = FixupAppExecuteRemove(coresys)

    assert app_execute_remove.auto is False

    coresys.resolution.add_suggestion(
        Suggestion(
            SuggestionType.EXECUTE_REMOVE,
            ContextType.ADDON,
            reference=install_app_ssh.slug,
        )
    )
    coresys.resolution.add_issue(
        Issue(
            IssueType.DETACHED_ADDON_REMOVED,
            ContextType.ADDON,
            reference=install_app_ssh.slug,
        )
    )

    with patch.object(App, "uninstall") as uninstall:
        await app_execute_remove()

        assert uninstall.called

    assert len(coresys.resolution.suggestions) == 0
    assert len(coresys.resolution.issues) == 0


async def test_fixup_deprecated_arch_app(coresys: CoreSys, install_app_ssh: App):
    """Test fixup for deprecated arch app issue."""
    app_execute_remove = FixupAppExecuteRemove(coresys)

    coresys.resolution.add_suggestion(
        Suggestion(
            SuggestionType.EXECUTE_REMOVE,
            ContextType.ADDON,
            reference=install_app_ssh.slug,
        )
    )
    coresys.resolution.add_issue(
        Issue(
            IssueType.DEPRECATED_ARCH_ADDON,
            ContextType.ADDON,
            reference=install_app_ssh.slug,
        )
    )

    with patch.object(App, "uninstall") as uninstall:
        await app_execute_remove()

        assert uninstall.called

    assert len(coresys.resolution.suggestions) == 0
    assert len(coresys.resolution.issues) == 0
