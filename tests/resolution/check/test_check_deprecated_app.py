"""Test check for deprecated apps."""

from unittest.mock import patch

from supervisor.apps.app import App
from supervisor.const import AppStage, CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.checks.deprecated_app import CheckDeprecatedApp
from supervisor.resolution.const import ContextType, IssueType


async def test_base(coresys: CoreSys):
    """Test check basics."""
    deprecated_app = CheckDeprecatedApp(coresys)
    assert deprecated_app.slug == "deprecated_addon"
    assert deprecated_app.enabled


async def test_check(coresys: CoreSys, install_app_ssh: App):
    """Test check for deprecated apps."""
    deprecated_app = CheckDeprecatedApp(coresys)
    await coresys.core.set_state(CoreState.SETUP)

    await deprecated_app()
    assert len(coresys.resolution.issues) == 0

    # Mock test app as deprecated
    install_app_ssh.data["stage"] = AppStage.DEPRECATED

    await deprecated_app()

    assert len(coresys.resolution.issues) == 1
    assert coresys.resolution.issues[0].type is IssueType.DEPRECATED_ADDON
    assert coresys.resolution.issues[0].context is ContextType.ADDON
    assert coresys.resolution.issues[0].reference == install_app_ssh.slug
    assert len(coresys.resolution.suggestions) == 1


async def test_approve(coresys: CoreSys, install_app_ssh: App):
    """Test approve existing deprecated app issues."""
    deprecated_app = CheckDeprecatedApp(coresys)
    await coresys.core.set_state(CoreState.SETUP)

    assert await deprecated_app.approve_check(reference=install_app_ssh.slug) is False

    # Mock test app as deprecated
    install_app_ssh.data["stage"] = AppStage.DEPRECATED

    assert await deprecated_app.approve_check(reference=install_app_ssh.slug) is True


async def test_did_run(coresys: CoreSys):
    """Test that the check ran as expected."""
    deprecated_app = CheckDeprecatedApp(coresys)
    should_run = deprecated_app.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert should_run == [CoreState.SETUP]
    assert len(should_not_run) != 0

    with patch.object(CheckDeprecatedApp, "run_check", return_value=None) as check:
        for state in should_run:
            await coresys.core.set_state(state)
            await deprecated_app()
            check.assert_called_once()
            check.reset_mock()

        for state in should_not_run:
            await coresys.core.set_state(state)
            await deprecated_app()
            check.assert_not_called()
            check.reset_mock()
