"""Test check for add-ons with deprecated architectures."""

from unittest.mock import patch

from supervisor.addons.addon import Addon
from supervisor.const import AddonStage, CoreState
from supervisor.coresys import CoreSys
from supervisor.resolution.checks.deprecated_arch_addon import CheckDeprecatedArchAddon
from supervisor.resolution.const import ContextType, IssueType, SuggestionType


async def test_base(coresys: CoreSys):
    """Test check basics."""
    deprecated_arch_addon = CheckDeprecatedArchAddon(coresys)
    assert deprecated_arch_addon.slug == "deprecated_arch_addon"
    assert deprecated_arch_addon.enabled


async def test_check(coresys: CoreSys, install_addon_ssh: Addon):
    """Test check for installed add-ons with deprecated architectures."""
    deprecated_arch_addon = CheckDeprecatedArchAddon(coresys)
    await coresys.core.set_state(CoreState.SETUP)

    await deprecated_arch_addon()
    assert len(coresys.resolution.issues) == 0

    install_addon_ssh.data["arch"] = ["armv7"]

    await deprecated_arch_addon()

    assert len(coresys.resolution.issues) == 1
    assert coresys.resolution.issues[0].type is IssueType.DEPRECATED_ARCH_ADDON
    assert coresys.resolution.issues[0].context is ContextType.ADDON
    assert coresys.resolution.issues[0].reference == install_addon_ssh.slug
    assert len(coresys.resolution.suggestions) == 1
    assert coresys.resolution.suggestions[0].type is SuggestionType.EXECUTE_REMOVE


async def test_check_ignores_mixed_supported_arch(
    coresys: CoreSys, install_addon_ssh: Addon
):
    """Test check does not create issue when a supported arch is still present."""
    deprecated_arch_addon = CheckDeprecatedArchAddon(coresys)
    await coresys.core.set_state(CoreState.SETUP)

    install_addon_ssh.data["arch"] = ["armv7", "amd64"]

    await deprecated_arch_addon()

    assert len(coresys.resolution.issues) == 0


async def test_check_deprecated_machine(coresys: CoreSys, install_addon_ssh: Addon):
    """Test check for installed add-ons using deprecated machine entries."""
    deprecated_arch_addon = CheckDeprecatedArchAddon(coresys)
    await coresys.core.set_state(CoreState.SETUP)

    install_addon_ssh.data["machine"] = ["raspberrypi3"]

    await deprecated_arch_addon()

    assert len(coresys.resolution.issues) == 1
    assert coresys.resolution.issues[0].type is IssueType.DEPRECATED_ARCH_ADDON
    assert coresys.resolution.suggestions[0].type is SuggestionType.EXECUTE_REMOVE


async def test_check_ignores_mixed_supported_machine(
    coresys: CoreSys, install_addon_ssh: Addon
):
    """Test check does not create issue when current machine is still supported."""
    deprecated_arch_addon = CheckDeprecatedArchAddon(coresys)
    await coresys.core.set_state(CoreState.SETUP)

    install_addon_ssh.data["machine"] = ["raspberrypi3", install_addon_ssh.sys_machine]

    await deprecated_arch_addon()

    assert len(coresys.resolution.issues) == 0


async def test_check_ignores_stage_deprecated(
    coresys: CoreSys, install_addon_ssh: Addon
):
    """Test check does not create arch repair issue for already deprecated add-ons."""
    deprecated_arch_addon = CheckDeprecatedArchAddon(coresys)
    await coresys.core.set_state(CoreState.SETUP)

    install_addon_ssh.data["stage"] = AddonStage.DEPRECATED
    install_addon_ssh.data["arch"] = ["armv7"]

    await deprecated_arch_addon()

    assert len(coresys.resolution.issues) == 0


async def test_approve(coresys: CoreSys, install_addon_ssh: Addon):
    """Test approve existing deprecated arch addon issues."""
    deprecated_arch_addon = CheckDeprecatedArchAddon(coresys)
    await coresys.core.set_state(CoreState.SETUP)

    assert (
        await deprecated_arch_addon.approve_check(reference=install_addon_ssh.slug)
        is False
    )

    install_addon_ssh.data["arch"] = ["armv7"]

    assert (
        await deprecated_arch_addon.approve_check(reference=install_addon_ssh.slug)
        is True
    )

    install_addon_ssh.data["arch"] = ["armv7", "amd64"]

    assert (
        await deprecated_arch_addon.approve_check(reference=install_addon_ssh.slug)
        is False
    )

    install_addon_ssh.data["arch"] = ["amd64"]
    install_addon_ssh.data["machine"] = ["raspberrypi3"]

    assert (
        await deprecated_arch_addon.approve_check(reference=install_addon_ssh.slug)
        is True
    )

    install_addon_ssh.data["machine"] = ["raspberrypi3", install_addon_ssh.sys_machine]

    assert (
        await deprecated_arch_addon.approve_check(reference=install_addon_ssh.slug)
        is False
    )

    install_addon_ssh.data["stage"] = AddonStage.DEPRECATED

    assert (
        await deprecated_arch_addon.approve_check(reference=install_addon_ssh.slug)
        is False
    )


async def test_did_run(coresys: CoreSys):
    """Test that the check ran as expected."""
    deprecated_arch_addon = CheckDeprecatedArchAddon(coresys)
    should_run = deprecated_arch_addon.states
    should_not_run = [state for state in CoreState if state not in should_run]
    assert should_run == [CoreState.SETUP, CoreState.RUNNING]
    assert len(should_not_run) != 0

    with patch.object(
        CheckDeprecatedArchAddon, "run_check", return_value=None
    ) as check:
        for state in should_run:
            await coresys.core.set_state(state)
            await deprecated_arch_addon()
            check.assert_called_once()
            check.reset_mock()

        for state in should_not_run:
            await coresys.core.set_state(state)
            await deprecated_arch_addon()
            check.assert_not_called()
            check.reset_mock()
