"""Test check for deprecated addons."""

from unittest.mock import patch

from supervisor.addons.addon import Addon
from supervisor.const import AddonStage, CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.checks.deprecated_addon import CheckDeprecatedAddon
from supervisor.resolution.const import ContextType, IssueType


async def test_base(coresys: CoreSys):
    """Test check basics."""
    deprecated_addon = CheckDeprecatedAddon(coresys)
    assert deprecated_addon.slug == "deprecated_addon"
    assert deprecated_addon.enabled


async def test_check(coresys: CoreSys, install_addon_ssh: Addon):
    """Test check for deprecated addons."""
    deprecated_addon = CheckDeprecatedAddon(coresys)
    await coresys.core.set_state(CoreState.SETUP)

    await deprecated_addon()
    assert len(coresys.resolution.issues) == 0

    # Mock test addon as deprecated
    install_addon_ssh.data["stage"] = AddonStage.DEPRECATED

    await deprecated_addon()

    assert len(coresys.resolution.issues) == 1
    assert coresys.resolution.issues[0].type is IssueType.DEPRECATED_ADDON
    assert coresys.resolution.issues[0].context is ContextType.ADDON
    assert coresys.resolution.issues[0].reference == install_addon_ssh.slug
    assert len(coresys.resolution.suggestions) == 1


async def test_approve(coresys: CoreSys, install_addon_ssh: Addon):
    """Test approve existing deprecated addon issues."""
    deprecated_addon = CheckDeprecatedAddon(coresys)
    await coresys.core.set_state(CoreState.SETUP)

    assert (
        await deprecated_addon.approve_check(reference=install_addon_ssh.slug) is False
    )

    # Mock test addon as deprecated
    install_addon_ssh.data["stage"] = AddonStage.DEPRECATED

    assert (
        await deprecated_addon.approve_check(reference=install_addon_ssh.slug) is True
    )


async def test_did_run(coresys: CoreSys):
    """Test that the check ran as expected."""
    deprecated_addon = CheckDeprecatedAddon(coresys)
    should_run = deprecated_addon.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert should_run == [CoreState.SETUP]
    assert len(should_not_run) != 0

    with patch.object(CheckDeprecatedAddon, "run_check", return_value=None) as check:
        for state in should_run:
            await coresys.core.set_state(state)
            await deprecated_addon()
            check.assert_called_once()
            check.reset_mock()

        for state in should_not_run:
            await coresys.core.set_state(state)
            await deprecated_addon()
            check.assert_not_called()
            check.reset_mock()
