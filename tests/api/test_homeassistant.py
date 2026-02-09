"""Test homeassistant api."""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, PropertyMock, patch

from aiodocker.containers import DockerContainer
from aiohttp.test_utils import TestClient
from awesomeversion import AwesomeVersion
import pytest

from supervisor.backups.manager import BackupManager
from supervisor.const import DNS_SUFFIX, CoreState
from supervisor.coresys import CoreSys
from supervisor.docker.homeassistant import DockerHomeAssistant
from supervisor.docker.interface import DockerInterface
from supervisor.homeassistant.api import APIState, HomeAssistantAPI
from supervisor.homeassistant.const import WSEvent
from supervisor.homeassistant.core import HomeAssistantCore
from supervisor.homeassistant.module import HomeAssistant
from supervisor.resolution.const import ContextType, IssueType
from supervisor.resolution.data import Issue

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


async def test_api_stats(api_client: TestClient, container: DockerContainer):
    """Test stats."""
    container.show.return_value["State"]["Status"] = "running"
    container.show.return_value["State"]["Running"] = True
    container.stats = AsyncMock(
        return_value=[load_json_fixture("container_stats.json")]
    )

    resp = await api_client.get("/homeassistant/stats")
    assert resp.status == 200
    result = await resp.json()
    assert result["data"]["cpu_percent"] == 90.0
    assert result["data"]["memory_usage"] == 59700000
    assert result["data"]["memory_limit"] == 4000000000
    assert result["data"]["memory_percent"] == 1.49


async def test_api_set_options(api_client: TestClient):
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
    api_client: TestClient, container: DockerContainer, tmp_supervisor_data: Path
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


@pytest.mark.usefixtures("path_extern")
async def test_api_rebuild(
    api_client: TestClient,
    coresys: CoreSys,
    container: DockerContainer,
    tmp_supervisor_data: Path,
):
    """Test rebuilding homeassistant."""
    coresys.homeassistant.version = AwesomeVersion("2023.09.0")
    safe_mode_marker = tmp_supervisor_data / "homeassistant" / "safe-mode"

    with patch.object(HomeAssistantCore, "_block_till_run"):
        await api_client.post("/homeassistant/rebuild")

    assert container.delete.call_count == 2
    container.start.assert_called_once()
    assert not safe_mode_marker.exists()

    with patch.object(HomeAssistantCore, "_block_till_run"):
        await api_client.post("/homeassistant/rebuild", json={"safe_mode": True})

    assert container.delete.call_count == 4
    assert container.start.call_count == 2
    assert safe_mode_marker.exists()


@pytest.mark.parametrize("action", ["rebuild", "restart", "stop", "update"])
async def test_migration_blocks_stopping_core(
    api_client: TestClient, coresys: CoreSys, action: str
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
        patch.object(HomeAssistantAPI, "check_frontend_available", return_value=True),
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
    # Count-based progress: 2 layers need pulling (each worth 50%)
    # Layers that already exist are excluded from progress calculation
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
            "progress": 9.2,
            "done": False,
        },
        {
            "stage": None,
            "progress": 25.6,
            "done": False,
        },
        {
            "stage": None,
            "progress": 35.4,
            "done": False,
        },
    ]
    assert events[-5:] == [
        {
            "stage": None,
            "progress": 95.5,
            "done": False,
        },
        {
            "stage": None,
            "progress": 96.9,
            "done": False,
        },
        {
            "stage": None,
            "progress": 98.2,
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


@pytest.mark.usefixtures("path_extern")
async def test_config_check(
    api_client: TestClient, coresys: CoreSys, container: DockerContainer
):
    """Test config check API."""
    coresys.homeassistant.version = AwesomeVersion("2025.1.0")

    result = await api_client.post("/core/check")
    assert result.status == 200

    coresys.docker.containers.create.assert_called_once_with(
        {
            "Image": "ghcr.io/home-assistant/qemux86-64-homeassistant:2025.1.0",
            "Labels": {"supervisor_managed": ""},
            "OpenStdin": False,
            "StdinOnce": False,
            "AttachStdin": False,
            "AttachStdout": False,
            "AttachStderr": False,
            "HostConfig": {
                "NetworkMode": "hassio",
                "Init": True,
                "Privileged": True,
                "Mounts": [
                    {
                        "Type": "bind",
                        "Source": "/mnt/data/supervisor/homeassistant",
                        "Target": "/config",
                        "ReadOnly": False,
                    },
                    {
                        "Type": "bind",
                        "Source": "/mnt/data/supervisor/ssl",
                        "Target": "/ssl",
                        "ReadOnly": True,
                    },
                    {
                        "Type": "bind",
                        "Source": "/mnt/data/supervisor/share",
                        "Target": "/share",
                        "ReadOnly": False,
                    },
                ],
                "Dns": [str(coresys.docker.network.dns)],
                "DnsSearch": [DNS_SUFFIX],
                "DnsOptions": ["timeout:10"],
            },
            "Env": ["TZ=Etc/UTC"],
            "Entrypoint": [],
            "Cmd": [
                "python3",
                "-m",
                "homeassistant",
                "-c",
                "/config",
                "--script",
                "check_config",
            ],
        },
        name=None,
    )
    container.start.assert_called_once()


@pytest.mark.usefixtures("path_extern")
async def test_config_check_error(api_client: TestClient, container: DockerContainer):
    """Test config check API strips color coding from log output on error."""
    container.log.return_value = [
        "\x1b[36mTest logs 1\x1b[0m",
        "\x1b[36mTest logs 2\x1b[0m",
    ]
    container.wait.return_value = {"StatusCode": 1}

    result = await api_client.post("/core/check")
    assert result.status == 400
    resp = await result.json()
    assert resp["message"] == "Test logs 1\nTest logs 2"


async def test_update_frontend_check_success(api_client: TestClient, coresys: CoreSys):
    """Test that update succeeds when frontend check passes."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
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
        patch.object(HomeAssistantAPI, "check_frontend_available", return_value=True),
    ):
        resp = await api_client.post("/core/update", json={"version": "2025.8.3"})

    assert resp.status == 200


async def test_update_frontend_check_fails_triggers_rollback(
    api_client: TestClient,
    coresys: CoreSys,
    caplog: pytest.LogCaptureFixture,
    tmp_supervisor_data: Path,
):
    """Test that update triggers rollback when frontend check fails."""
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    coresys.homeassistant.version = AwesomeVersion("2025.8.0")

    # Mock successful first update, failed frontend check, then successful rollback
    update_call_count = 0

    async def mock_update(*args, **kwargs):
        nonlocal update_call_count
        update_call_count += 1
        if update_call_count == 1:
            # First update succeeds
            coresys.homeassistant.version = AwesomeVersion("2025.8.3")
        elif update_call_count == 2:
            # Rollback succeeds
            coresys.homeassistant.version = AwesomeVersion("2025.8.0")

    with (
        patch.object(DockerInterface, "update", new=mock_update),
        patch.object(
            DockerHomeAssistant,
            "version",
            new=PropertyMock(return_value=AwesomeVersion("2025.8.0")),
        ),
        patch.object(
            HomeAssistantAPI, "get_config", return_value={"components": ["frontend"]}
        ),
        patch.object(HomeAssistantAPI, "check_frontend_available", return_value=False),
    ):
        resp = await api_client.post("/core/update", json={"version": "2025.8.3"})

    # Update should trigger rollback, which succeeds and returns 200
    assert resp.status == 200
    assert "Frontend component loaded but frontend is not accessible" in caplog.text
    assert "HomeAssistant update failed -> rollback!" in caplog.text
    # Should have called update twice (once for update, once for rollback)
    assert update_call_count == 2
    # An update_rollback issue should be created
    assert (
        Issue(IssueType.UPDATE_ROLLBACK, ContextType.CORE) in coresys.resolution.issues
    )
