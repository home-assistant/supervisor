"""Test fixup app disable boot."""

from supervisor.apps.app import App
from supervisor.const import AppBoot
from supervisor.coresys import CoreSys
from supervisor.resolution.const import SuggestionType
from supervisor.resolution.fixups.app_disable_boot import FixupAppDisableBoot

from tests.apps.test_manager import BOOT_FAIL_ISSUE


async def test_fixup(coresys: CoreSys, install_app_ssh: App):
    """Test fixup disables boot."""
    install_app_ssh.boot = AppBoot.AUTO
    app_disable_boot = FixupAppDisableBoot(coresys)
    assert app_disable_boot.auto is False

    coresys.resolution.add_issue(
        BOOT_FAIL_ISSUE,
        suggestions=[SuggestionType.DISABLE_BOOT],
    )
    await app_disable_boot()

    assert install_app_ssh.boot == AppBoot.MANUAL
    assert not coresys.resolution.issues
    assert not coresys.resolution.suggestions


async def test_fixup_no_app(coresys: CoreSys):
    """Test fixup dismisses if app is missing."""
    app_disable_boot = FixupAppDisableBoot(coresys)

    coresys.resolution.add_issue(
        BOOT_FAIL_ISSUE,
        suggestions=[SuggestionType.DISABLE_BOOT],
    )
    await app_disable_boot()

    assert not coresys.resolution.issues
    assert not coresys.resolution.suggestions
