"""Test homeassistant api."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from aiohttp.test_utils import TestClient
from awesomeversion import AwesomeVersion
import pytest

from supervisor.coresys import CoreSys
from supervisor.homeassistant.api import APIState
from supervisor.homeassistant.core import HomeAssistantCore
from supervisor.homeassistant.module import HomeAssistant

from tests.api import common_test_api_advanced_logs
from tests.common import load_json_fixture


@pytest.mark.parametrize("legacy_route", [True, False])
async def test_api_core_logs(
    api_client: TestClient, journald_logs: MagicMock, legacy_route: bool
):
    """Test core logs."""
    await common_test_api_advanced_logs(
        f"/{'homeassistant' if legacy_route else 'core'}",
        "homeassistant",
        api_client,
        journald_logs,
    )


async def test_api_stats(api_client: TestClient, coresys: CoreSys):
    """Test stats."""
    coresys.docker.containers.get.return_value.status = "running"
    coresys.docker.containers.get.return_value.stats.return_value = load_json_fixture(
        "container_stats.json"
    )

    resp = await api_client.get("/homeassistant/stats")
    assert resp.status == 200
    result = await resp.json()
    assert result["data"]["cpu_percent"] == 90.0
    assert result["data"]["memory_usage"] == 59700000
    assert result["data"]["memory_limit"] == 4000000000
    assert result["data"]["memory_percent"] == 1.49


async def test_api_set_options(api_client: TestClient, coresys: CoreSys):
    """Test setting options for homeassistant."""
    resp = await api_client.get("/homeassistant/info")
    assert resp.status == 200
    result = await resp.json()
    assert result["data"]["watchdog"] is True
    assert result["data"]["backups_exclude_database"] is False

    with patch.object(HomeAssistant, "save_data") as save_data:
        resp = await api_client.post(
            "/homeassistant/options",
            json={"backups_exclude_database": True, "watchdog": False},
        )
        assert resp.status == 200
        save_data.assert_called_once()

    resp = await api_client.get("/homeassistant/info")
    assert resp.status == 200
    result = await resp.json()
    assert result["data"]["watchdog"] is False
    assert result["data"]["backups_exclude_database"] is True


async def test_api_set_image(api_client: TestClient, coresys: CoreSys):
    """Test changing the image for homeassistant."""
    assert (
        coresys.homeassistant.image == "ghcr.io/home-assistant/qemux86-64-homeassistant"
    )
    assert coresys.homeassistant.override_image is False

    with patch.object(HomeAssistant, "save_data"):
        resp = await api_client.post(
            "/homeassistant/options",
            json={"image": "test_image"},
        )

    assert resp.status == 200
    assert coresys.homeassistant.image == "test_image"
    assert coresys.homeassistant.override_image is True

    with patch.object(HomeAssistant, "save_data"):
        resp = await api_client.post(
            "/homeassistant/options",
            json={"image": "ghcr.io/home-assistant/qemux86-64-homeassistant"},
        )

    assert resp.status == 200
    assert (
        coresys.homeassistant.image == "ghcr.io/home-assistant/qemux86-64-homeassistant"
    )
    assert coresys.homeassistant.override_image is False


async def test_api_restart(
    api_client: TestClient,
    container: MagicMock,
    tmp_supervisor_data: Path,
):
    """Test restarting homeassistant."""
    safe_mode_marker = tmp_supervisor_data / "homeassistant" / "safe-mode"

    with patch.object(HomeAssistantCore, "_block_till_run"):
        await api_client.post("/homeassistant/restart")

    container.restart.assert_called_once()
    assert not safe_mode_marker.exists()

    with patch.object(HomeAssistantCore, "_block_till_run"):
        await api_client.post("/homeassistant/restart", json={"safe_mode": True})

    assert container.restart.call_count == 2
    assert safe_mode_marker.exists()


async def test_api_rebuild(
    api_client: TestClient,
    coresys: CoreSys,
    container: MagicMock,
    tmp_supervisor_data: Path,
    path_extern,
):
    """Test rebuilding homeassistant."""
    coresys.homeassistant.version = AwesomeVersion("2023.09.0")
    safe_mode_marker = tmp_supervisor_data / "homeassistant" / "safe-mode"

    with patch.object(HomeAssistantCore, "_block_till_run"):
        await api_client.post("/homeassistant/rebuild")

    assert container.remove.call_count == 2
    container.start.assert_called_once()
    assert not safe_mode_marker.exists()

    with patch.object(HomeAssistantCore, "_block_till_run"):
        await api_client.post("/homeassistant/rebuild", json={"safe_mode": True})

    assert container.remove.call_count == 4
    assert container.start.call_count == 2
    assert safe_mode_marker.exists()


@pytest.mark.parametrize("action", ["rebuild", "restart", "stop", "update"])
async def test_migration_blocks_stopping_core(
    api_client: TestClient,
    coresys: CoreSys,
    action: str,
):
    """Test that an offline db migration in progress stops users from stopping/restarting core."""
    coresys.homeassistant.api.get_api_state.return_value = APIState("NOT_RUNNING", True)

    resp = await api_client.post(f"/homeassistant/{action}")
    assert resp.status == 503
    result = await resp.json()
    assert (
        result["message"]
        == "Offline database migration in progress, try again after it has completed"
    )


async def test_force_rebuild_during_migration(api_client: TestClient, coresys: CoreSys):
    """Test force option rebuilds even during a migration."""
    coresys.homeassistant.api.get_api_state.return_value = APIState("NOT_RUNNING", True)

    with patch.object(HomeAssistantCore, "rebuild") as rebuild:
        await api_client.post("/homeassistant/rebuild", json={"force": True})
        rebuild.assert_called_once()


async def test_force_restart_during_migration(api_client: TestClient, coresys: CoreSys):
    """Test force option restarts even during a migration."""
    coresys.homeassistant.api.get_api_state.return_value = APIState("NOT_RUNNING", True)

    with patch.object(HomeAssistantCore, "restart") as restart:
        await api_client.post("/homeassistant/restart", json={"force": True})
        restart.assert_called_once()


async def test_force_stop_during_migration(api_client: TestClient, coresys: CoreSys):
    """Test force option stops even during a migration."""
    coresys.homeassistant.api.get_api_state.return_value = APIState("NOT_RUNNING", True)

    with patch.object(HomeAssistantCore, "stop") as stop:
        await api_client.post("/homeassistant/stop", json={"force": True})
        stop.assert_called_once()
