"""Test check for detached apps due to repo missing."""

from unittest.mock import patch

from supervisor.apps.app import App
from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.checks.detached_app_missing import CheckDetachedAppMissing
from supervisor.resolution.const import ContextType, IssueType
from supervisor.resolution.data import Issue


async def test_base(coresys: CoreSys):
    """Test check basics."""
    detached_app_missing = CheckDetachedAppMissing(coresys)
    assert detached_app_missing.slug == "detached_addon_missing"
    assert detached_app_missing.enabled


async def test_check(coresys: CoreSys, install_app_ssh: App):
    """Test check for detached apps."""
    detached_app_missing = CheckDetachedAppMissing(coresys)
    await coresys.core.set_state(CoreState.SETUP)

    await detached_app_missing()
    assert len(coresys.resolution.issues) == 0

    # Mock test app was been installed from a now non-existent store
    install_app_ssh.slug = "abc123_ssh"
    coresys.apps.data.system["abc123_ssh"] = coresys.apps.data.system["local_ssh"]
    coresys.apps.local["abc123_ssh"] = coresys.apps.local["local_ssh"]
    install_app_ssh.data["repository"] = "abc123"

    await detached_app_missing()

    assert len(coresys.resolution.issues) == 1
    assert coresys.resolution.issues[0].type is IssueType.DETACHED_ADDON_MISSING
    assert coresys.resolution.issues[0].context is ContextType.ADDON
    assert coresys.resolution.issues[0].reference == install_app_ssh.slug
    assert len(coresys.resolution.suggestions) == 0


async def test_approve(coresys: CoreSys, install_app_ssh: App):
    """Test approve existing detached app issues."""
    detached_app_missing = CheckDetachedAppMissing(coresys)
    await coresys.core.set_state(CoreState.SETUP)

    assert (
        await detached_app_missing.approve_check(
            Issue(
                IssueType.DETACHED_ADDON_MISSING,
                ContextType.ADDON,
                reference=install_app_ssh.slug,
            )
        )
        is False
    )

    # Mock test app was been installed from a now non-existent store
    install_app_ssh.slug = "abc123_ssh"
    coresys.apps.data.system["abc123_ssh"] = coresys.apps.data.system["local_ssh"]
    coresys.apps.local["abc123_ssh"] = coresys.apps.local["local_ssh"]
    install_app_ssh.data["repository"] = "abc123"

    assert (
        await detached_app_missing.approve_check(
            Issue(
                IssueType.DETACHED_ADDON_MISSING,
                ContextType.ADDON,
                reference=install_app_ssh.slug,
            )
        )
        is True
    )


async def test_did_run(coresys: CoreSys):
    """Test that the check ran as expected."""
    detached_app_missing = CheckDetachedAppMissing(coresys)
    should_run = detached_app_missing.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert should_run == [CoreState.SETUP]
    assert len(should_not_run) != 0

    with patch.object(CheckDetachedAppMissing, "run_check", return_value=None) as check:
        for state in should_run:
            await coresys.core.set_state(state)
            await detached_app_missing()
            check.assert_called_once()
            check.reset_mock()

        for state in should_not_run:
            await coresys.core.set_state(state)
            await detached_app_missing()
            check.assert_not_called()
            check.reset_mock()
