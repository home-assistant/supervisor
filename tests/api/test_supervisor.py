"""Test Supervisor API."""
# pylint: disable=protected-access
import pytest

from supervisor.api.const import ATTR_AVAILABLE_UPDATES
from supervisor.coresys import CoreSys

from tests.const import TEST_ADDON_SLUG


@pytest.mark.asyncio
async def test_api_supervisor_options_debug(api_client, coresys: CoreSys):
    """Test security options force security."""
    assert not coresys.config.debug

    await api_client.post("/supervisor/options", json={"debug": True})

    assert coresys.config.debug


@pytest.mark.asyncio
async def test_api_supervisor_available_updates(
    install_addon_ssh,
    api_client,
    coresys: CoreSys,
):
    """Test available_updates."""
    installed_addon = coresys.addons.get(TEST_ADDON_SLUG)
    installed_addon.persist["version"] = "1.2.3"

    async def available_updates():
        return (await (await api_client.get("/supervisor/available_updates")).json())[
            "data"
        ][ATTR_AVAILABLE_UPDATES]

    updates = await available_updates()
    assert len(updates) == 1
    assert updates[-1] == {
        "icon": None,
        "name": "Terminal & SSH",
        "panel_path": "/update-available/local_ssh",
        "update_path": "/addons/local_ssh/update",
        "update_type": "addon",
        "version": "1.2.3",
        "version_latest": "9.2.1",
    }

    coresys.updater._data["hassos"] = "321"
    coresys.os._version = "123"
    updates = await available_updates()
    assert len(updates) == 2
    assert updates[0] == {
        "panel_path": "/update-available/os",
        "update_path": "/os/update",
        "update_type": "os",
        "version": "123",
        "version_latest": "321",
    }

    coresys.updater._data["homeassistant"] = "321"
    coresys.homeassistant.version = "123"
    updates = await available_updates()
    assert len(updates) == 3
    assert updates[0] == {
        "panel_path": "/update-available/core",
        "update_path": "/core/update",
        "update_type": "core",
        "version": "123",
        "version_latest": "321",
    }
