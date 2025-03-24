"""Test check for detached addons due to repo missing."""

from unittest.mock import patch

from supervisor.addons.addon import Addon
from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.checks.detached_addon_missing import (
    CheckDetachedAddonMissing,
)
from supervisor.resolution.const import ContextType, IssueType


async def test_base(coresys: CoreSys):
    """Test check basics."""
    detached_addon_missing = CheckDetachedAddonMissing(coresys)
    assert detached_addon_missing.slug == "detached_addon_missing"
    assert detached_addon_missing.enabled


async def test_check(coresys: CoreSys, install_addon_ssh: Addon):
    """Test check for detached addons."""
    detached_addon_missing = CheckDetachedAddonMissing(coresys)
    await coresys.core.set_state(CoreState.SETUP)

    await detached_addon_missing()
    assert len(coresys.resolution.issues) == 0

    # Mock test addon was been installed from a now non-existent store
    install_addon_ssh.slug = "abc123_ssh"
    coresys.addons.data.system["abc123_ssh"] = coresys.addons.data.system["local_ssh"]
    coresys.addons.local["abc123_ssh"] = coresys.addons.local["local_ssh"]
    install_addon_ssh.data["repository"] = "abc123"

    await detached_addon_missing()

    assert len(coresys.resolution.issues) == 1
    assert coresys.resolution.issues[0].type is IssueType.DETACHED_ADDON_MISSING
    assert coresys.resolution.issues[0].context is ContextType.ADDON
    assert coresys.resolution.issues[0].reference == install_addon_ssh.slug
    assert len(coresys.resolution.suggestions) == 0


async def test_approve(coresys: CoreSys, install_addon_ssh: Addon):
    """Test approve existing detached addon issues."""
    detached_addon_missing = CheckDetachedAddonMissing(coresys)
    await coresys.core.set_state(CoreState.SETUP)

    assert (
        await detached_addon_missing.approve_check(reference=install_addon_ssh.slug)
        is False
    )

    # Mock test addon was been installed from a now non-existent store
    install_addon_ssh.slug = "abc123_ssh"
    coresys.addons.data.system["abc123_ssh"] = coresys.addons.data.system["local_ssh"]
    coresys.addons.local["abc123_ssh"] = coresys.addons.local["local_ssh"]
    install_addon_ssh.data["repository"] = "abc123"

    assert (
        await detached_addon_missing.approve_check(reference=install_addon_ssh.slug)
        is True
    )


async def test_did_run(coresys: CoreSys):
    """Test that the check ran as expected."""
    detached_addon_missing = CheckDetachedAddonMissing(coresys)
    should_run = detached_addon_missing.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert should_run == [CoreState.SETUP]
    assert len(should_not_run) != 0

    with patch.object(
        CheckDetachedAddonMissing, "run_check", return_value=None
    ) as check:
        for state in should_run:
            await coresys.core.set_state(state)
            await detached_addon_missing()
            check.assert_called_once()
            check.reset_mock()

        for state in should_not_run:
            await coresys.core.set_state(state)
            await detached_addon_missing()
            check.assert_not_called()
            check.reset_mock()
