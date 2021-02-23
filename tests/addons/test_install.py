"""Test add-on install."""
# pylint: disable=protected-access
import pytest

from supervisor.coresys import CoreSys
from supervisor.exceptions import AddonsNotSupportedError
from supervisor.store.addon import AddonStore


async def test_addon_not_available_arch(coresys: CoreSys, caplog):
    """Test exception when arch is not supported."""
    addon = AddonStore(coresys, "test_addon")
    coresys.addons.store = {addon.slug: addon}
    coresys.arch._supported_arch = ["amd64"]
    coresys.store.data.addons = {addon.slug: {"arch": ["armv7"]}}

    with pytest.raises(
        AddonsNotSupportedError, match="Architecture is not supported by the add-on"
    ):
        await coresys.addons.install(addon.slug)

    coresys.arch._supported_arch = ["amd64"]
    coresys.store.data.addons = {
        addon.slug: {
            "arch": ["amd64"],
            "machine": ["i836"],
        }
    }

    assert "Add-on test_addon not supported on that platform" in caplog.text
    caplog.clear()

    with pytest.raises(
        AddonsNotSupportedError, match="Architecture is not supported by the add-on"
    ):
        await coresys.addons.install(addon.slug)

    assert "Add-on test_addon not supported on that platform" in caplog.text


async def test_addon_not_available_homeassistant(coresys: CoreSys, caplog):
    """Test exception when homeassistant version is not supported."""
    addon = AddonStore(coresys, "test_addon")
    coresys.addons.store = {addon.slug: addon}
    coresys.arch._supported_arch = ["amd64"]
    coresys.homeassistant.version = "1"
    coresys.store.data.addons = {
        addon.slug: {
            "arch": ["amd64"],
            "machine": ["qemux86-64"],
            "homeassistant": "2",
        }
    }

    with pytest.raises(
        AddonsNotSupportedError,
        match="Home Assistant version is not supported by the add-on",
    ):
        await coresys.addons.install(addon.slug)

    assert "Add-on test_addon not supported on that platform" in caplog.text
