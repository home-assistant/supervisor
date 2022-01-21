"""Test Supervisor API."""
# pylint: disable=protected-access
from unittest.mock import AsyncMock

import pytest

from supervisor.api.const import ATTR_AVAILABLE_UPDATES
from supervisor.coresys import CoreSys

from tests.const import TEST_ADDON_SLUG


@pytest.mark.asyncio
async def test_api_info(api_client):
    """Test docker info api."""
    resp = await api_client.get("/info")
    result = await resp.json()

    assert result["data"]["supervisor"] == "DEV"
    assert result["data"]["docker"] == "1.0.0"
    assert result["data"]["supported"] == True
    assert result["data"]["channel"] == "stable"
    assert result["data"]["logging"] == "info"
    assert result["data"]["timezone"] == "UTC"


@pytest.mark.asyncio
async def test_api_available_updates(
    install_addon_ssh,
    api_client,
    coresys: CoreSys,
):
    """Test available_updates."""
    installed_addon = coresys.addons.get(TEST_ADDON_SLUG)
    installed_addon.persist["version"] = "1.2.3"

    async def available_updates():
        return (await (await api_client.get("/available_updates")).json())["data"][
            ATTR_AVAILABLE_UPDATES
        ]

    updates = await available_updates()
    assert len(updates) == 1
    assert updates[-1] == {
        "icon": None,
        "name": "Terminal & SSH",
        "panel_path": "/update-available/local_ssh",
        "update_type": "addon",
        "version_latest": "9.2.1",
    }

    coresys.updater._data["hassos"] = "321"
    coresys.os._version = "123"
    updates = await available_updates()
    assert len(updates) == 2
    assert updates[0] == {
        "panel_path": "/update-available/os",
        "update_type": "os",
        "version_latest": "321",
    }

    coresys.updater._data["homeassistant"] = "321"
    coresys.homeassistant.version = "123"
    updates = await available_updates()
    assert len(updates) == 3
    assert updates[0] == {
        "panel_path": "/update-available/core",
        "update_type": "core",
        "version_latest": "321",
    }


@pytest.mark.asyncio
async def test_api_refresh_updates(api_client, coresys: CoreSys):
    """Test docker info api."""

    coresys.updater.reload = AsyncMock()
    coresys.store.reload = AsyncMock()

    resp = await api_client.post("/refresh_updates")
    assert resp.status == 200

    assert coresys.updater.reload.called
    assert coresys.store.reload.called
