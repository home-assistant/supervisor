"""Test homeassistant api."""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

from aiohttp.test_utils import TestClient
from awesomeversion import AwesomeVersion
import pytest

from supervisor.backups.manager import BackupManager
from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.docker.homeassistant import DockerHomeAssistant
from supervisor.docker.interface import DockerInterface
from supervisor.homeassistant.api import APIState, HomeAssistantAPI
from supervisor.homeassistant.const import WSEvent
from supervisor.homeassistant.core import HomeAssistantCore
from supervisor.homeassistant.module import HomeAssistant

from tests.common import AsyncIterator, load_json_fixture


@pytest.mark.parametrize("legacy_route", [True, False])
async def test_api_core_logs(
    advanced_logs_tester: AsyncMock,
    legacy_route: bool,
):
    """Test core logs."""
    await advanced_logs_tester(
        f"/{'homeassistant' if legacy_route else 'core'}",
        "homeassistant",
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


@pytest.mark.parametrize(
    ("make_backup", "backup_called", "update_called"),
    [(True, True, False), (False, False, True)],
)
async def test_home_assistant_background_update(
    api_client: TestClient,
    coresys: CoreSys,
    make_backup: bool,
    backup_called: bool,
    update_called: bool,
):
    """Test background update of Home Assistant."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    event = asyncio.Event()
    mock_update_called = mock_backup_called = False

    # Mock backup/update as long-running tasks
    async def mock_docker_interface_update(*args, **kwargs):
        nonlocal mock_update_called
        mock_update_called = True
        await event.wait()

    async def mock_partial_backup(*args, **kwargs):
        nonlocal mock_backup_called
        mock_backup_called = True
        await event.wait()

    with (
        patch.object(DockerInterface, "update", new=mock_docker_interface_update),
        patch.object(BackupManager, "do_backup_partial", new=mock_partial_backup),
        patch.object(
            DockerInterface,
            "version",
            new=PropertyMock(return_value=AwesomeVersion("2025.8.0")),
        ),
    ):
        resp = await api_client.post(
            "/core/update",
            json={"background": True, "backup": make_backup, "version": "2025.8.3"},
        )

    assert mock_backup_called is backup_called
    assert mock_update_called is update_called

    assert resp.status == 200
    body = await resp.json()
    assert (job := coresys.jobs.get_job(body["data"]["job_id"]))
    assert job.name == "home_assistant_core_update"
    event.set()


async def test_background_home_assistant_update_fails_fast(
    api_client: TestClient, coresys: CoreSys
):
    """Test background Home Assistant update returns error not job if validation doesn't succeed."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    with (
        patch.object(
            DockerInterface,
            "version",
            new=PropertyMock(return_value=AwesomeVersion("2025.8.3")),
        ),
    ):
        resp = await api_client.post(
            "/core/update",
            json={"background": True, "version": "2025.8.3"},
        )

    assert resp.status == 400
    body = await resp.json()
    assert body["message"] == "Version 2025.8.3 is already installed"


@pytest.mark.usefixtures("tmp_supervisor_data")
async def test_api_progress_updates_home_assistant_update(
    api_client: TestClient, coresys: CoreSys, ha_ws_client: AsyncMock
):
    """Test progress updates sent to Home Assistant for updates."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    coresys.core.set_state(CoreState.RUNNING)

    logs = load_json_fixture("docker_pull_image_log.json")
    coresys.docker.images.pull.return_value = AsyncIterator(logs)
    coresys.homeassistant.version = AwesomeVersion("2025.8.0")

    with (
        patch.object(
            DockerHomeAssistant,
            "version",
            new=PropertyMock(return_value=AwesomeVersion("2025.8.0")),
        ),
        patch.object(
            HomeAssistantAPI, "get_config", return_value={"components": ["frontend"]}
        ),
    ):
        resp = await api_client.post("/core/update", json={"version": "2025.8.3"})

    assert resp.status == 200

    events = [
        {
            "stage": evt.args[0]["data"]["data"]["stage"],
            "progress": evt.args[0]["data"]["data"]["progress"],
            "done": evt.args[0]["data"]["data"]["done"],
        }
        for evt in ha_ws_client.async_send_command.call_args_list
        if "data" in evt.args[0]
        and evt.args[0]["data"]["event"] == WSEvent.JOB
        and evt.args[0]["data"]["data"]["name"] == "home_assistant_core_update"
    ]
    assert events[:5] == [
        {
            "stage": None,
            "progress": 0,
            "done": None,
        },
        {
            "stage": None,
            "progress": 0,
            "done": False,
        },
        {
            "stage": None,
            "progress": 0.1,
            "done": False,
        },
        {
            "stage": None,
            "progress": 1.2,
            "done": False,
        },
        {
            "stage": None,
            "progress": 2.8,
            "done": False,
        },
    ]
    assert events[-5:] == [
        {
            "stage": None,
            "progress": 97.2,
            "done": False,
        },
        {
            "stage": None,
            "progress": 98.4,
            "done": False,
        },
        {
            "stage": None,
            "progress": 99.4,
            "done": False,
        },
        {
            "stage": None,
            "progress": 100,
            "done": False,
        },
        {
            "stage": None,
            "progress": 100,
            "done": True,
        },
    ]
