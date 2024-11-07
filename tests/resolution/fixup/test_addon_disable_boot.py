"""Test fixup addon disable boot."""

from supervisor.addons.addon import Addon
from supervisor.const import AddonBoot
from supervisor.coresys import CoreSys
from supervisor.resolution.const import SuggestionType
from supervisor.resolution.fixups.addon_disable_boot import FixupAddonDisableBoot

from tests.addons.test_manager import BOOT_FAIL_ISSUE


async def test_fixup(coresys: CoreSys, install_addon_ssh: Addon):
    """Test fixup disables boot."""
    install_addon_ssh.boot = AddonBoot.AUTO
    addon_disable_boot = FixupAddonDisableBoot(coresys)
    assert addon_disable_boot.auto is False

    coresys.resolution.add_issue(
        BOOT_FAIL_ISSUE,
        suggestions=[SuggestionType.DISABLE_BOOT],
    )
    await addon_disable_boot()

    assert install_addon_ssh.boot == AddonBoot.MANUAL
    assert not coresys.resolution.issues
    assert not coresys.resolution.suggestions


async def test_fixup_no_addon(coresys: CoreSys):
    """Test fixup dismisses if addon is missing."""
    addon_disable_boot = FixupAddonDisableBoot(coresys)

    coresys.resolution.add_issue(
        BOOT_FAIL_ISSUE,
        suggestions=[SuggestionType.DISABLE_BOOT],
    )
    await addon_disable_boot()

    assert not coresys.resolution.issues
    assert not coresys.resolution.suggestions
