"""Test check for detached apps due to removal from repo."""

from pathlib import Path
from unittest.mock import PropertyMock, patch

from supervisor.apps.app import App
from supervisor.config import CoreConfig
from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.checks.detached_app_removed import CheckDetachedAppRemoved
from supervisor.resolution.const import ContextType, IssueType, SuggestionType


async def test_base(coresys: CoreSys):
    """Test check basics."""
    detached_app_removed = CheckDetachedAppRemoved(coresys)
    assert detached_app_removed.slug == "detached_addon_removed"
    assert detached_app_removed.enabled


async def test_check(coresys: CoreSys, install_app_ssh: App, tmp_supervisor_data: Path):
    """Test check for detached apps."""
    detached_app_removed = CheckDetachedAppRemoved(coresys)
    await coresys.core.set_state(CoreState.SETUP)

    await detached_app_removed()
    assert len(coresys.resolution.issues) == 0
    assert len(coresys.resolution.suggestions) == 0

    (apps_dir := tmp_supervisor_data / "apps" / "local").mkdir(parents=True)
    with patch.object(
        CoreConfig, "path_apps_local", new=PropertyMock(return_value=apps_dir)
    ):
        await coresys.store.load()

    await detached_app_removed()

    assert len(coresys.resolution.issues) == 1
    assert coresys.resolution.issues[0].type is IssueType.DETACHED_ADDON_REMOVED
    assert coresys.resolution.issues[0].context is ContextType.ADDON
    assert coresys.resolution.issues[0].reference == install_app_ssh.slug

    assert len(coresys.resolution.suggestions) == 1
    assert coresys.resolution.suggestions[0].type is SuggestionType.EXECUTE_REMOVE
    assert coresys.resolution.suggestions[0].context is ContextType.ADDON
    assert coresys.resolution.suggestions[0].reference == install_app_ssh.slug


async def test_approve(
    coresys: CoreSys, install_app_ssh: App, tmp_supervisor_data: Path
):
    """Test approve existing detached app issues."""
    detached_app_removed = CheckDetachedAppRemoved(coresys)
    await coresys.core.set_state(CoreState.SETUP)

    assert (
        await detached_app_removed.approve_check(reference=install_app_ssh.slug)
        is False
    )

    (apps_dir := tmp_supervisor_data / "apps" / "local").mkdir(parents=True)
    with patch.object(
        CoreConfig, "path_apps_local", new=PropertyMock(return_value=apps_dir)
    ):
        await coresys.store.load()

    assert (
        await detached_app_removed.approve_check(reference=install_app_ssh.slug) is True
    )


async def test_did_run(coresys: CoreSys):
    """Test that the check ran as expected."""
    detached_app_removed = CheckDetachedAppRemoved(coresys)
    should_run = detached_app_removed.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert should_run == [CoreState.SETUP]
    assert len(should_not_run) != 0

    with patch.object(CheckDetachedAppRemoved, "run_check", return_value=None) as check:
        for state in should_run:
            await coresys.core.set_state(state)
            await detached_app_removed()
            check.assert_called_once()
            check.reset_mock()

        for state in should_not_run:
            await coresys.core.set_state(state)
            await detached_app_removed()
            check.assert_not_called()
            check.reset_mock()
