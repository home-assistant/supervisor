"""Test backups API."""

import asyncio
from pathlib import Path, PurePath
from shutil import copy
from typing import Any
from unittest.mock import ANY, AsyncMock, MagicMock, PropertyMock, patch

from aiohttp import MultipartWriter
from aiohttp.test_utils import TestClient
from awesomeversion import AwesomeVersion
import pytest

from supervisor.addons.addon import Addon
from supervisor.backups.backup import Backup, BackupLocation
from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.docker.manager import DockerAPI
from supervisor.exceptions import (
    AddonsError,
    BackupInvalidError,
    HomeAssistantBackupError,
)
from supervisor.homeassistant.core import HomeAssistantCore
from supervisor.homeassistant.module import HomeAssistant
from supervisor.homeassistant.websocket import HomeAssistantWebSocket
from supervisor.mounts.mount import Mount
from supervisor.supervisor import Supervisor

from tests.common import get_fixture_path
from tests.const import TEST_ADDON_SLUG


@pytest.mark.usefixtures("mock_full_backup")
async def test_info(api_client: TestClient, coresys: CoreSys, tmp_path: Path):
    """Test info endpoint."""
    copy(get_fixture_path("backup_example.tar"), tmp_path / "test_backup.tar")

    resp = await api_client.get("/backups/info")
    result = await resp.json()
    assert result["data"]["days_until_stale"] == 30
    assert len(result["data"]["backups"]) == 1
    assert result["data"]["backups"][0]["slug"] == "test"
    assert result["data"]["backups"][0]["content"]["homeassistant"] is True
    assert len(result["data"]["backups"][0]["content"]["addons"]) == 1
    assert result["data"]["backups"][0]["content"]["addons"][0] == "local_ssh"
    assert result["data"]["backups"][0]["size"] == 0.01
    assert result["data"]["backups"][0]["size_bytes"] == 10240


@pytest.mark.usefixtures("mock_full_backup")
async def test_backup_more_info(
    api_client: TestClient, coresys: CoreSys, tmp_path: Path
):
    """Test info endpoint."""
    copy(get_fixture_path("backup_example.tar"), tmp_path / "test_backup.tar")

    resp = await api_client.get("/backups/test/info")
    result = await resp.json()
    assert result["data"]["slug"] == "test"
    assert result["data"]["homeassistant"] == "2022.8.0"
    assert len(result["data"]["addons"]) == 1
    assert result["data"]["addons"][0] == {
        "name": "SSH",
        "size": 0,
        "slug": "local_ssh",
        "version": "1.0.0",
    }
    assert result["data"]["size"] == 0.01
    assert result["data"]["size_bytes"] == 10240
    assert result["data"]["homeassistant_exclude_database"] is False


@pytest.mark.usefixtures("mock_full_backup")
async def test_list(api_client: TestClient, coresys: CoreSys, tmp_path: Path):
    """Test list endpoint."""
    copy(get_fixture_path("backup_example.tar"), tmp_path / "test_backup.tar")

    resp = await api_client.get("/backups")
    result = await resp.json()
    assert len(result["data"]["backups"]) == 1
    assert result["data"]["backups"][0]["slug"] == "test"
    assert result["data"]["backups"][0]["content"]["homeassistant"] is True
    assert len(result["data"]["backups"][0]["content"]["addons"]) == 1
    assert result["data"]["backups"][0]["content"]["addons"][0] == "local_ssh"
    assert result["data"]["backups"][0]["size"] == 0.01
    assert result["data"]["backups"][0]["size_bytes"] == 10240


async def test_options(api_client: TestClient, coresys: CoreSys):
    """Test options endpoint."""
    assert coresys.backups.days_until_stale == 30

    with patch.object(type(coresys.backups), "save_data") as save_data:
        await api_client.post(
            "/backups/options",
            json={
                "days_until_stale": 10,
            },
        )
        save_data.assert_called_once()

    assert coresys.backups.days_until_stale == 10


@pytest.mark.parametrize(
    ("location", "backup_dir", "api_location"),
    [
        ("backup_test", PurePath("mounts", "backup_test"), "backup_test"),
        (None, PurePath("backup"), None),
        ("", PurePath("backup"), None),
        (".local", PurePath("backup"), None),
    ],
)
@pytest.mark.usefixtures("path_extern", "mount_propagation", "mock_is_mount")
async def test_backup_to_location(
    api_client: TestClient,
    coresys: CoreSys,
    location: str | None,
    backup_dir: PurePath,
    api_location: str | None,
    tmp_supervisor_data: Path,
):
    """Test making a backup to a specific location with default mount."""
    await coresys.mounts.load()
    (coresys.config.path_mounts / "backup_test").mkdir()
    mount = Mount.from_dict(
        coresys,
        {
            "name": "backup_test",
            "type": "cifs",
            "usage": "backup",
            "server": "backup.local",
            "share": "backups",
        },
    )
    await coresys.mounts.create_mount(mount)
    coresys.mounts.default_backup_mount = mount

    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    resp = await api_client.post(
        "/backups/new/full",
        json={
            "name": "Mount test",
            "location": location,
        },
    )
    result = await resp.json()
    assert result["result"] == "ok"
    slug = result["data"]["slug"]

    assert (tmp_supervisor_data / backup_dir / f"{slug}.tar").exists()

    resp = await api_client.get(f"/backups/{slug}/info")
    result = await resp.json()
    assert result["result"] == "ok"
    assert result["data"]["location"] == api_location


@pytest.mark.usefixtures(
    "tmp_supervisor_data", "path_extern", "mount_propagation", "mock_is_mount"
)
async def test_backup_to_default(api_client: TestClient, coresys: CoreSys):
    """Test making backup to default mount."""
    await coresys.mounts.load()
    (mount_dir := coresys.config.path_mounts / "backup_test").mkdir()
    mount = Mount.from_dict(
        coresys,
        {
            "name": "backup_test",
            "type": "cifs",
            "usage": "backup",
            "server": "backup.local",
            "share": "backups",
        },
    )
    await coresys.mounts.create_mount(mount)
    coresys.mounts.default_backup_mount = mount

    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    resp = await api_client.post(
        "/backups/new/full",
        json={"name": "Mount test"},
    )
    result = await resp.json()
    assert result["result"] == "ok"
    slug = result["data"]["slug"]

    assert (mount_dir / f"{slug}.tar").exists()


@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
async def test_api_freeze_thaw(
    api_client: TestClient, coresys: CoreSys, ha_ws_client: AsyncMock
):
    """Test manual freeze and thaw for external backup via API."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    ha_ws_client.ha_version = AwesomeVersion("2022.1.0")

    await api_client.post("/backups/freeze")
    assert coresys.core.state == CoreState.FREEZE
    await asyncio.sleep(0)
    assert any(
        call.args[0] == {"type": "backup/start"}
        for call in ha_ws_client.async_send_command.call_args_list
    )

    ha_ws_client.async_send_command.reset_mock()
    await api_client.post("/backups/thaw")
    assert coresys.core.state == CoreState.RUNNING
    await asyncio.sleep(0)
    assert any(
        call.args[0] == {"type": "backup/end"}
        for call in ha_ws_client.async_send_command.call_args_list
    )


@pytest.mark.parametrize(
    "partial_backup,exclude_db_setting",
    [(False, True), (True, True), (False, False), (True, False)],
)
@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
async def test_api_backup_exclude_database(
    api_client: TestClient,
    coresys: CoreSys,
    partial_backup: bool,
    exclude_db_setting: bool,
):
    """Test backups exclude the database when specified."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    coresys.homeassistant.version = AwesomeVersion("2023.09.0")
    coresys.homeassistant.backups_exclude_database = exclude_db_setting

    json = {} if exclude_db_setting else {"homeassistant_exclude_database": True}
    with patch.object(HomeAssistant, "backup") as backup:
        if partial_backup:
            resp = await api_client.post(
                "/backups/new/partial", json={"homeassistant": True} | json
            )
        else:
            resp = await api_client.post("/backups/new/full", json=json)

        backup.assert_awaited_once_with(ANY, True)
        assert resp.status == 200


async def _get_job_info(api_client: TestClient, job_id: str) -> dict[str, Any]:
    """Test background job progress and block until it is done."""
    resp = await api_client.get(f"/jobs/{job_id}")
    assert resp.status == 200
    result = await resp.json()
    return result["data"]


@pytest.mark.parametrize(
    "backup_type,options",
    [
        ("full", {}),
        (
            "partial",
            {
                "homeassistant": True,
                "folders": ["addons/local", "media", "share", "ssl"],
            },
        ),
    ],
)
@pytest.mark.usefixtures("path_extern")
async def test_api_backup_restore_background(
    api_client: TestClient,
    coresys: CoreSys,
    backup_type: str,
    options: dict[str, Any],
    tmp_supervisor_data: Path,
    supervisor_internet: AsyncMock,
):
    """Test background option on backup/restore APIs."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    coresys.homeassistant.version = AwesomeVersion("2023.09.0")
    (tmp_supervisor_data / "addons/local").mkdir(parents=True)

    assert coresys.jobs.jobs == []

    resp = await api_client.post(
        f"/backups/new/{backup_type}",
        json={"background": True, "name": f"{backup_type} backup"} | options,
    )
    assert resp.status == 200
    result = await resp.json()
    job_id = result["data"]["job_id"]
    assert (await _get_job_info(api_client, job_id))["done"] is False

    while not (job := (await _get_job_info(api_client, job_id)))["done"]:
        await asyncio.sleep(0)

    assert job["name"] == f"backup_manager_{backup_type}_backup"
    assert (backup_slug := job["reference"])
    assert job["child_jobs"][0]["name"] == "backup_store_homeassistant"
    assert job["child_jobs"][0]["reference"] == backup_slug
    assert job["child_jobs"][1]["name"] == "backup_store_folders"
    assert job["child_jobs"][1]["reference"] == backup_slug
    assert {j["reference"] for j in job["child_jobs"][1]["child_jobs"]} == {
        "addons/local",
        "media",
        "share",
        "ssl",
    }

    with patch.object(HomeAssistantCore, "start"):
        resp = await api_client.post(
            f"/backups/{backup_slug}/restore/{backup_type}",
            json={"background": True} | options,
        )
        assert resp.status == 200
        result = await resp.json()
        job_id = result["data"]["job_id"]
        assert (await _get_job_info(api_client, job_id))["done"] is False

        while not (job := (await _get_job_info(api_client, job_id)))["done"]:
            await asyncio.sleep(0)

    assert job["name"] == f"backup_manager_{backup_type}_restore"
    assert job["reference"] == backup_slug
    assert job["child_jobs"][0]["name"] == "backup_restore_folders"
    assert job["child_jobs"][0]["reference"] == backup_slug
    assert {j["reference"] for j in job["child_jobs"][0]["child_jobs"]} == {
        "addons/local",
        "media",
        "share",
        "ssl",
    }
    assert job["child_jobs"][1]["name"] == "backup_restore_homeassistant"
    assert job["child_jobs"][1]["reference"] == backup_slug

    if backup_type == "full":
        assert job["child_jobs"][2]["name"] == "backup_remove_delta_addons"
        assert job["child_jobs"][2]["reference"] == backup_slug


@pytest.mark.parametrize(
    "backup_type,options",
    [
        ("full", {}),
        (
            "partial",
            {
                "homeassistant": True,
                "folders": ["addons/local", "media", "share", "ssl"],
                "addons": ["local_ssh"],
            },
        ),
    ],
)
@pytest.mark.usefixtures("install_addon_ssh", "path_extern")
async def test_api_backup_errors(
    api_client: TestClient,
    coresys: CoreSys,
    backup_type: str,
    options: dict[str, Any],
    tmp_supervisor_data: Path,
):
    """Test error reporting in backup job."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    coresys.homeassistant.version = AwesomeVersion("2023.09.0")
    (tmp_supervisor_data / "addons/local").mkdir(parents=True)

    assert coresys.jobs.jobs == []

    with patch.object(
        Addon, "backup", side_effect=(err := AddonsError("Backup error"))
    ):
        resp = await api_client.post(
            f"/backups/new/{backup_type}",
            json={"name": f"{backup_type} backup"} | options,
        )

    assert resp.status == 200
    result = await resp.json()
    job_id = result["data"]["job_id"]
    slug = result["data"]["slug"]
    job = await _get_job_info(api_client, job_id)

    assert job["name"] == f"backup_manager_{backup_type}_backup"
    assert job["done"] is True
    assert job["reference"] == slug
    assert job["errors"] == []
    assert job["child_jobs"][0]["name"] == "backup_store_homeassistant"
    assert job["child_jobs"][0]["reference"] == slug
    assert job["child_jobs"][1]["name"] == "backup_store_addons"
    assert job["child_jobs"][1]["reference"] == slug
    assert job["child_jobs"][1]["child_jobs"][0]["name"] == "backup_addon_save"
    assert job["child_jobs"][1]["child_jobs"][0]["reference"] == "local_ssh"
    assert job["child_jobs"][1]["child_jobs"][0]["errors"] == [
        {
            "type": "BackupError",
            "message": str(err),
            "stage": None,
        }
    ]
    assert job["child_jobs"][2]["name"] == "backup_store_folders"
    assert job["child_jobs"][2]["reference"] == slug
    assert {j["reference"] for j in job["child_jobs"][2]["child_jobs"]} == {
        "addons/local",
        "media",
        "share",
        "ssl",
    }

    with (
        patch.object(
            HomeAssistant,
            "backup",
            side_effect=HomeAssistantBackupError("Backup error"),
        ),
        patch.object(Addon, "backup"),
    ):
        resp = await api_client.post(
            f"/backups/new/{backup_type}",
            json={"name": f"{backup_type} backup"} | options,
        )

    assert resp.status == 400
    result = await resp.json()
    job_id = result["job_id"]
    job = await _get_job_info(api_client, job_id)

    assert job["name"] == f"backup_manager_{backup_type}_backup"
    assert job["done"] is True
    assert job["errors"] == [
        {
            "type": "HomeAssistantBackupError",
            "message": "Backup error",
            "stage": "home_assistant",
        }
    ]
    assert job["child_jobs"][0]["name"] == "backup_store_homeassistant"
    assert job["child_jobs"][0]["errors"] == [
        {
            "type": "HomeAssistantBackupError",
            "message": "Backup error",
            "stage": None,
        }
    ]
    assert len(job["child_jobs"]) == 1


async def test_backup_immediate_errors(api_client: TestClient, coresys: CoreSys):
    """Test backup errors that return immediately even in background mode."""
    await coresys.core.set_state(CoreState.FREEZE)
    resp = await api_client.post(
        "/backups/new/full",
        json={"name": "Test", "background": True},
    )
    assert resp.status == 400
    assert "freeze" in (await resp.json())["message"]

    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 0.5
    resp = await api_client.post(
        "/backups/new/partial",
        json={"name": "Test", "homeassistant": True, "background": True},
    )
    assert resp.status == 400
    assert "not enough free space" in (await resp.json())["message"]


async def test_restore_immediate_errors(
    request: pytest.FixtureRequest,
    api_client: TestClient,
    coresys: CoreSys,
    mock_partial_backup: Backup,
    supervisor_internet: AsyncMock,
):
    """Test restore errors that return immediately even in background mode."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    resp = await api_client.post(
        f"/backups/{mock_partial_backup.slug}/restore/full", json={"background": True}
    )
    assert resp.status == 400
    assert "only a partial backup" in (await resp.json())["message"]

    with (
        patch.object(Backup, "validate_backup"),
        patch.object(
            Backup,
            "supervisor_version",
            new=PropertyMock(return_value=AwesomeVersion("2024.01.0")),
        ),
        patch.object(
            Supervisor,
            "version",
            new=PropertyMock(return_value=AwesomeVersion("2023.12.0")),
        ),
    ):
        resp = await api_client.post(
            f"/backups/{mock_partial_backup.slug}/restore/partial",
            json={"background": True, "homeassistant": True},
        )
    assert resp.status == 400
    assert "Must update supervisor" in (await resp.json())["message"]

    with (
        patch.object(
            Backup,
            "all_locations",
            new={None: BackupLocation(path=Path("/"), protected=True, size_bytes=0)},
        ),
        patch.object(
            Backup,
            "validate_backup",
            side_effect=BackupInvalidError("Invalid password"),
        ),
    ):
        resp = await api_client.post(
            f"/backups/{mock_partial_backup.slug}/restore/partial",
            json={"background": True, "homeassistant": True},
        )
    assert resp.status == 400
    assert "Invalid password" in (await resp.json())["message"]

    with (
        patch.object(Backup, "validate_backup"),
        patch.object(Backup, "homeassistant", new=PropertyMock(return_value=None)),
    ):
        resp = await api_client.post(
            f"/backups/{mock_partial_backup.slug}/restore/partial",
            json={"background": True, "homeassistant": True},
        )
    assert resp.status == 400
    assert "No Home Assistant" in (await resp.json())["message"]

    resp = await api_client.post(
        f"/backups/{mock_partial_backup.slug}/restore/partial",
        json={"background": True, "folders": ["ssl"]},
    )
    assert resp.status == 404
    assert "file does not exist" in (await resp.json())["message"]


@pytest.mark.parametrize(
    ("folder", "location"), [("backup", None), ("core/backup", ".cloud_backup")]
)
async def test_reload(
    request: pytest.FixtureRequest,
    api_client: TestClient,
    coresys: CoreSys,
    tmp_supervisor_data: Path,
    folder: str,
    location: str | None,
):
    """Test backups reload."""
    assert not coresys.backups.list_backups

    backup_file = get_fixture_path("backup_example.tar")
    copy(backup_file, tmp_supervisor_data / folder)

    resp = await api_client.post("/backups/reload")
    assert resp.status == 200

    assert len(coresys.backups.list_backups) == 1
    assert (backup := coresys.backups.get("7fed74c8"))
    assert backup.location == location
    assert backup.locations == [location]


@pytest.mark.usefixtures("install_addon_ssh")
@pytest.mark.parametrize("api_client", [TEST_ADDON_SLUG], indirect=True)
async def test_cloud_backup_core_only(api_client: TestClient, mock_full_backup: Backup):
    """Test only core can access cloud backup location."""
    resp = await api_client.post(
        "/backups/new/full",
        json={
            "name": "Mount test",
            "location": ".cloud_backup",
        },
    )
    assert resp.status == 403

    resp = await api_client.post(
        "/backups/new/partial",
        json={"name": "Test", "homeassistant": True, "location": ".cloud_backup"},
    )
    assert resp.status == 403

    # pylint: disable-next=protected-access
    mock_full_backup._locations = {
        ".cloud_backup": BackupLocation(
            path=Path("/"), protected=False, size_bytes=10240
        )
    }
    assert mock_full_backup.location == ".cloud_backup"

    resp = await api_client.post(f"/backups/{mock_full_backup.slug}/restore/full")
    assert resp.status == 403

    resp = await api_client.post(
        f"/backups/{mock_full_backup.slug}/restore/partial",
        json={"homeassistant": True},
    )
    assert resp.status == 403

    resp = await api_client.delete(f"/backups/{mock_full_backup.slug}")
    assert resp.status == 403

    resp = await api_client.get(f"/backups/{mock_full_backup.slug}/download")
    assert resp.status == 403


async def test_upload_download(
    api_client: TestClient, coresys: CoreSys, tmp_supervisor_data: Path
):
    """Test upload and download of a backup."""
    # Capture our backup initially
    backup_file = get_fixture_path("backup_example.tar")
    backup = Backup(coresys, backup_file, "in", None)
    await backup.load()

    # Upload it and confirm it matches what we had
    with backup_file.open("rb") as file, MultipartWriter("form-data") as mp:
        mp.append(file)
        resp = await api_client.post("/backups/new/upload", data=mp)

    assert resp.status == 200
    body = await resp.json()
    assert body["data"]["slug"] == "7fed74c8"
    assert backup == coresys.backups.get("7fed74c8")

    # Download it and confirm it against the original again
    resp = await api_client.get("/backups/7fed74c8/download")
    assert resp.status == 200
    out_file = tmp_supervisor_data / "backup_example.tar"
    with out_file.open("wb") as out:
        out.write(await resp.read())

    out_backup = Backup(coresys, out_file, "out", None)
    await out_backup.load()
    assert backup == out_backup


@pytest.mark.usefixtures("path_extern", "tmp_supervisor_data")
@pytest.mark.parametrize(
    ("backup_type", "inputs", "locations"),
    [
        ("full", {}, [None, ".cloud_backup"]),
        ("full", {}, [".cloud_backup", None]),
        ("partial", {"folders": ["ssl"]}, [None, ".cloud_backup"]),
        ("partial", {"folders": ["ssl"]}, [".cloud_backup", None]),
    ],
)
async def test_backup_to_multiple_locations(
    api_client: TestClient,
    coresys: CoreSys,
    backup_type: str,
    inputs: dict[str, Any],
    locations: list[str | None],
):
    """Test making a backup to multiple locations."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    resp = await api_client.post(
        f"/backups/new/{backup_type}",
        json={"name": "Multiple locations test", "location": locations} | inputs,
    )
    assert resp.status == 200
    result = await resp.json()
    assert result["result"] == "ok"
    slug = result["data"]["slug"]

    orig_backup = coresys.config.path_backup / f"{slug}.tar"
    copy_backup = coresys.config.path_core_backup / f"{slug}.tar"
    assert orig_backup.exists()
    assert copy_backup.exists()
    assert coresys.backups.get(slug).all_locations == {
        None: BackupLocation(path=orig_backup, protected=False, size_bytes=10240),
        ".cloud_backup": BackupLocation(
            path=copy_backup, protected=False, size_bytes=10240
        ),
    }
    assert coresys.backups.get(slug).location is None


@pytest.mark.usefixtures("path_extern", "tmp_supervisor_data")
@pytest.mark.parametrize(
    ("backup_type", "inputs"), [("full", {}), ("partial", {"folders": ["ssl"]})]
)
async def test_backup_to_multiple_locations_error_on_copy(
    api_client: TestClient,
    coresys: CoreSys,
    backup_type: str,
    inputs: dict[str, Any],
):
    """Test making a backup to multiple locations that fails during copy stage."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    with patch("supervisor.backups.manager.copy", side_effect=OSError):
        resp = await api_client.post(
            f"/backups/new/{backup_type}",
            json={
                "name": "Multiple locations test",
                "location": [None, ".cloud_backup"],
            }
            | inputs,
        )
    assert resp.status == 200
    result = await resp.json()
    assert result["result"] == "ok"
    slug = result["data"]["slug"]

    orig_backup = coresys.config.path_backup / f"{slug}.tar"
    assert await coresys.run_in_executor(orig_backup.exists)
    assert coresys.backups.get(slug).all_locations == {
        None: BackupLocation(path=orig_backup, protected=False, size_bytes=10240),
    }
    assert coresys.backups.get(slug).location is None

    resp = await api_client.get("/jobs/info")
    assert resp.status == 200
    result = await resp.json()
    assert result["data"]["jobs"][0]["name"] == f"backup_manager_{backup_type}_backup"
    assert result["data"]["jobs"][0]["reference"] == slug
    assert result["data"]["jobs"][0]["done"] is True
    assert len(result["data"]["jobs"][0]["errors"]) == 0

    # Errors during copy to additional location should be recorded in child jobs only.
    assert (
        result["data"]["jobs"][0]["child_jobs"][-1]["name"]
        == "backup_copy_to_additional_locations"
    )
    assert (
        result["data"]["jobs"][0]["child_jobs"][-1]["child_jobs"][0]["name"]
        == "backup_copy_to_location"
    )
    assert (
        result["data"]["jobs"][0]["child_jobs"][-1]["child_jobs"][0]["reference"]
        == ".cloud_backup"
    )
    assert result["data"]["jobs"][0]["child_jobs"][-1]["child_jobs"][0]["errors"] == [
        {
            "type": "BackupError",
            "message": "Could not copy backup to .cloud_backup due to: ",
            "stage": None,
        }
    ]


@pytest.mark.parametrize(
    ("backup_type", "inputs"), [("full", {}), ("partial", {"folders": ["ssl"]})]
)
@pytest.mark.usefixtures("tmp_supervisor_data")
async def test_backup_with_extras(
    api_client: TestClient,
    coresys: CoreSys,
    backup_type: str,
    inputs: dict[str, Any],
):
    """Test backup including extra metdata."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    resp = await api_client.post(
        f"/backups/new/{backup_type}",
        json={"name": "Extras test", "extra": {"user": "test", "scheduled": True}}
        | inputs,
    )
    assert resp.status == 200
    result = await resp.json()
    assert result["result"] == "ok"
    slug = result["data"]["slug"]

    resp = await api_client.get(f"/backups/{slug}/info")
    assert resp.status == 200
    result = await resp.json()
    assert result["result"] == "ok"
    slug = result["data"]["extra"] == {"user": "test", "scheduled": True}


@pytest.mark.usefixtures("tmp_supervisor_data")
@pytest.mark.parametrize("local_location", ["", ".local"])
async def test_upload_to_multiple_locations(
    api_client: TestClient, coresys: CoreSys, local_location: str
):
    """Test uploading a backup to multiple locations."""
    backup_file = get_fixture_path("backup_example.tar")

    with backup_file.open("rb") as file, MultipartWriter("form-data") as mp:
        mp.append(file)
        resp = await api_client.post(
            f"/backups/new/upload?location={local_location}&location=.cloud_backup",
            data=mp,
        )

    assert resp.status == 200
    body = await resp.json()
    assert body["data"]["slug"] == "7fed74c8"

    orig_backup = coresys.config.path_backup / "7fed74c8.tar"
    copy_backup = coresys.config.path_core_backup / "7fed74c8.tar"
    assert orig_backup.exists()
    assert copy_backup.exists()
    assert coresys.backups.get("7fed74c8").all_locations == {
        None: BackupLocation(path=orig_backup, protected=False, size_bytes=10240),
        ".cloud_backup": BackupLocation(
            path=copy_backup, protected=False, size_bytes=10240
        ),
    }
    assert coresys.backups.get("7fed74c8").location is None


@pytest.mark.usefixtures("tmp_supervisor_data")
async def test_upload_duplicate_backup_new_location(
    api_client: TestClient, coresys: CoreSys
):
    """Test uploading a backup that already exists to a new location."""
    backup_file = get_fixture_path("backup_example.tar")
    orig_backup = Path(copy(backup_file, coresys.config.path_backup))
    await coresys.backups.reload()
    assert coresys.backups.get("7fed74c8").all_locations == {
        None: BackupLocation(path=orig_backup, protected=False, size_bytes=10240),
    }

    with backup_file.open("rb") as file, MultipartWriter("form-data") as mp:
        mp.append(file)
        resp = await api_client.post(
            "/backups/new/upload?location=.cloud_backup", data=mp
        )

    assert resp.status == 200
    body = await resp.json()
    assert body["data"]["slug"] == "7fed74c8"

    copy_backup = coresys.config.path_core_backup / "7fed74c8.tar"
    assert orig_backup.exists()
    assert copy_backup.exists()
    assert coresys.backups.get("7fed74c8").all_locations == {
        None: BackupLocation(path=orig_backup, protected=False, size_bytes=10240),
        ".cloud_backup": BackupLocation(
            path=copy_backup, protected=False, size_bytes=10240
        ),
    }
    assert coresys.backups.get("7fed74c8").location is None


@pytest.mark.parametrize(
    ("filename", "expected_status"),
    [("good.tar", 200), ("../bad.tar", 400), ("bad", 400)],
)
@pytest.mark.usefixtures("tmp_supervisor_data")
async def test_upload_with_filename(
    api_client: TestClient, coresys: CoreSys, filename: str, expected_status: int
):
    """Test uploading a backup to multiple locations."""
    backup_file = get_fixture_path("backup_example.tar")

    with backup_file.open("rb") as file, MultipartWriter("form-data") as mp:
        mp.append(file)
        resp = await api_client.post(
            f"/backups/new/upload?filename={filename}", data=mp
        )

    assert resp.status == expected_status
    body = await resp.json()
    if expected_status != 200:
        assert (
            body["message"]
            == r"does not match regular expression ^[^\\\/]+\.tar$."
            + f" Got '{filename}'"
        )
        return

    assert body["data"]["slug"] == "7fed74c8"

    orig_backup = coresys.config.path_backup / filename
    assert orig_backup.exists()
    assert coresys.backups.get("7fed74c8").all_locations == {
        None: BackupLocation(path=orig_backup, protected=False, size_bytes=10240),
    }
    assert coresys.backups.get("7fed74c8").location is None


@pytest.mark.parametrize(
    ("method", "url"),
    [
        ("get", "/backups/bad/info"),
        ("delete", "/backups/bad"),
        ("post", "/backups/bad/restore/full"),
        ("post", "/backups/bad/restore/partial"),
        ("get", "/backups/bad/download"),
    ],
)
async def test_backup_not_found(api_client: TestClient, method: str, url: str):
    """Test backup not found error."""
    resp = await api_client.request(method, url)
    assert resp.status == 404
    resp = await resp.json()
    assert resp["message"] == "Backup does not exist"


@pytest.mark.usefixtures("tmp_supervisor_data")
async def test_remove_backup_from_location(api_client: TestClient, coresys: CoreSys):
    """Test removing a backup from one location of multiple."""
    backup_file = get_fixture_path("backup_example.tar")
    location_1 = Path(copy(backup_file, coresys.config.path_backup))
    location_2 = Path(copy(backup_file, coresys.config.path_core_backup))

    await coresys.backups.reload()
    assert (backup := coresys.backups.get("7fed74c8"))
    assert backup.all_locations == {
        None: BackupLocation(path=location_1, protected=False, size_bytes=10240),
        ".cloud_backup": BackupLocation(
            path=location_2, protected=False, size_bytes=10240
        ),
    }

    resp = await api_client.delete(
        "/backups/7fed74c8", json={"location": ".cloud_backup"}
    )
    assert resp.status == 200

    assert location_1.exists()
    assert not location_2.exists()
    assert coresys.backups.get("7fed74c8")
    assert backup.all_locations == {
        None: BackupLocation(path=location_1, protected=False, size_bytes=10240),
    }


@pytest.mark.usefixtures("tmp_supervisor_data")
async def test_remove_backup_file_not_found(api_client: TestClient, coresys: CoreSys):
    """Test removing a backup from one location of multiple."""
    backup_file = get_fixture_path("backup_example.tar")
    location = Path(copy(backup_file, coresys.config.path_backup))

    await coresys.backups.reload()
    assert (backup := coresys.backups.get("7fed74c8"))
    assert backup.all_locations == {
        None: BackupLocation(path=location, protected=False, size_bytes=10240),
    }

    location.unlink()
    resp = await api_client.delete("/backups/7fed74c8")
    assert resp.status == 404
    body = await resp.json()
    assert (
        body["message"]
        == f"Cannot delete backup at {str(location)}, file does not exist!"
    )


@pytest.mark.parametrize("local_location", ["", ".local"])
async def test_download_backup_from_location(
    api_client: TestClient,
    coresys: CoreSys,
    tmp_supervisor_data: Path,
    local_location: str,
):
    """Test downloading a backup from a specific location."""
    backup_file = get_fixture_path("backup_example.tar")
    location_1 = Path(copy(backup_file, coresys.config.path_backup))
    location_2 = Path(copy(backup_file, coresys.config.path_core_backup))

    await coresys.backups.reload()
    assert (backup := coresys.backups.get("7fed74c8"))
    assert backup.all_locations == {
        None: BackupLocation(path=location_1, protected=False, size_bytes=10240),
        ".cloud_backup": BackupLocation(
            path=location_2, protected=False, size_bytes=10240
        ),
    }

    # The use case of this is user might want to pick a particular mount if one is flaky
    # To simulate this, remove the file from one location and show one works and the other doesn't
    assert backup.location is None
    location_2.unlink()

    resp = await api_client.get("/backups/7fed74c8/download?location=.cloud_backup")
    assert resp.status == 404

    resp = await api_client.get(f"/backups/7fed74c8/download?location={local_location}")
    assert resp.status == 200
    out_file = tmp_supervisor_data / "backup_example.tar"
    with out_file.open("wb") as out:
        out.write(await resp.read())

    out_backup = Backup(coresys, out_file, "out", None)
    await out_backup.load()
    assert backup == out_backup


@pytest.mark.usefixtures("mock_full_backup")
async def test_download_backup_from_invalid_location(api_client: TestClient):
    """Test error for invalid download location."""
    resp = await api_client.get("/backups/test/download?location=.cloud_backup")
    assert resp.status == 400
    body = await resp.json()
    assert body["message"] == "Backup test is not in location .cloud_backup"


@pytest.mark.usefixtures("tmp_supervisor_data")
async def test_partial_backup_all_addons(
    api_client: TestClient,
    coresys: CoreSys,
    install_addon_ssh: Addon,
):
    """Test backup including extra metdata."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    with patch.object(Backup, "store_addons") as store_addons:
        resp = await api_client.post(
            "/backups/new/partial", json={"name": "All addons test", "addons": "ALL"}
        )
        assert resp.status == 200
        store_addons.assert_called_once_with([install_addon_ssh])


@pytest.mark.parametrize("local_location", [None, "", ".local"])
async def test_restore_backup_from_location(
    api_client: TestClient,
    coresys: CoreSys,
    tmp_supervisor_data: Path,
    local_location: str | None,
    supervisor_internet: AsyncMock,
):
    """Test restoring a backup from a specific location."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    # Make a backup and a file to test with
    (test_file := coresys.config.path_share / "test.txt").touch()
    resp = await api_client.post(
        "/backups/new/partial",
        json={
            "name": "Test",
            "folders": ["share"],
            "location": [None, ".cloud_backup"],
        },
    )
    assert resp.status == 200
    body = await resp.json()
    backup = coresys.backups.get(body["data"]["slug"])
    assert set(backup.all_locations) == {None, ".cloud_backup"}

    # The use case of this is user might want to pick a particular mount if one is flaky
    # To simulate this, remove the file from one location and show one works and the other doesn't
    assert backup.location is None
    (backup_local_path := backup.all_locations[None].path).unlink()
    test_file.unlink()

    resp = await api_client.post(
        f"/backups/{backup.slug}/restore/partial",
        json={"location": local_location, "folders": ["share"]},
    )
    assert resp.status == 404
    body = await resp.json()
    assert (
        body["message"]
        == f"Cannot validate backup at {backup_local_path.as_posix()}, file does not exist!"
    )

    resp = await api_client.post(
        f"/backups/{backup.slug}/restore/partial",
        json={"location": ".cloud_backup", "folders": ["share"]},
    )
    assert resp.status == 200
    assert test_file.is_file()


@pytest.mark.usefixtures("tmp_supervisor_data")
async def test_restore_backup_unencrypted_after_encrypted(
    api_client: TestClient,
    coresys: CoreSys,
    supervisor_internet: AsyncMock,
):
    """Test restoring an unencrypted backup after an encrypted backup and vis-versa."""
    enc_tar = copy(get_fixture_path("test_consolidate.tar"), coresys.config.path_backup)
    unc_tar = copy(
        get_fixture_path("test_consolidate_unc.tar"), coresys.config.path_core_backup
    )
    await coresys.backups.reload()

    backup = coresys.backups.get("d9c48f8b")
    assert backup.all_locations == {
        None: BackupLocation(path=Path(enc_tar), protected=True, size_bytes=10240),
        ".cloud_backup": BackupLocation(
            path=Path(unc_tar),
            protected=False,
            size_bytes=10240,
        ),
    }

    # pylint: disable=fixme
    # TODO: There is a bug in the restore code that causes the restore to fail
    # if the backup contains a Docker registry configuration and one location
    # is encrypted and the other is not (just like our test fixture).
    # We punt the ball on this one for this PR since this is a rare edge case.
    backup.restore_dockerconfig = MagicMock()

    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    # Restore encrypted backup
    (test_file := coresys.config.path_ssl / "test.txt").touch()
    resp = await api_client.post(
        f"/backups/{backup.slug}/restore/partial",
        json={"location": None, "password": "test", "folders": ["ssl"]},
    )
    assert resp.status == 200
    body = await resp.json()
    assert body["result"] == "ok"
    assert not test_file.is_file()

    # Restore unencrypted backup
    test_file.touch()
    resp = await api_client.post(
        f"/backups/{backup.slug}/restore/partial",
        json={"location": ".cloud_backup", "folders": ["ssl"]},
    )
    assert resp.status == 200
    body = await resp.json()
    assert body["result"] == "ok"
    assert not test_file.is_file()

    # Restore encrypted backup
    test_file.touch()
    resp = await api_client.post(
        f"/backups/{backup.slug}/restore/partial",
        json={"location": None, "password": "test", "folders": ["ssl"]},
    )
    assert resp.status == 200
    body = await resp.json()
    assert body["result"] == "ok"
    assert not test_file.is_file()


@pytest.mark.parametrize(
    ("backup_type", "postbody"), [("partial", {"homeassistant": True}), ("full", {})]
)
@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
async def test_restore_homeassistant_adds_env(
    api_client: TestClient,
    coresys: CoreSys,
    docker: DockerAPI,
    backup_type: str,
    postbody: dict[str, Any],
    supervisor_internet: AsyncMock,
):
    """Test restoring home assistant from backup adds env to container."""
    event = asyncio.Event()
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    coresys.homeassistant.version = AwesomeVersion("2025.1.0")
    backup = await coresys.backups.do_backup_full()

    async def mock_async_send_message(_, message: dict[str, Any]):
        """Mock of async send message in ws client."""
        if (
            message["data"]["event"] == "job"
            and message["data"]["data"]["name"]
            == f"backup_manager_{backup_type}_restore"
            and message["data"]["data"]["reference"] == backup.slug
            and message["data"]["data"]["done"]
        ):
            event.set()

    with (
        patch.object(HomeAssistantCore, "_block_till_run"),
        patch.object(
            HomeAssistantWebSocket, "async_send_message", new=mock_async_send_message
        ),
    ):
        resp = await api_client.post(
            f"/backups/{backup.slug}/restore/{backup_type}",
            json={"background": True} | postbody,
        )
        assert resp.status == 200
        body = await resp.json()
        job = coresys.jobs.get_job(body["data"]["job_id"])

        if not job.done:
            await asyncio.wait_for(event.wait(), 5)

    assert docker.containers.create.call_args.kwargs["name"] == "homeassistant"
    assert (
        docker.containers.create.call_args.kwargs["environment"][
            "SUPERVISOR_RESTORE_JOB_ID"
        ]
        == job.uuid
    )


@pytest.mark.usefixtures("tmp_supervisor_data")
async def test_backup_mixed_encryption(api_client: TestClient, coresys: CoreSys):
    """Test a backup with mixed encryption status across locations."""
    enc_tar = copy(get_fixture_path("test_consolidate.tar"), coresys.config.path_backup)
    unc_tar = copy(
        get_fixture_path("test_consolidate_unc.tar"), coresys.config.path_core_backup
    )
    await coresys.backups.reload()

    backup = coresys.backups.get("d9c48f8b")
    assert backup.all_locations == {
        None: BackupLocation(path=Path(enc_tar), protected=True, size_bytes=10240),
        ".cloud_backup": BackupLocation(
            path=Path(unc_tar),
            protected=False,
            size_bytes=10240,
        ),
    }

    resp = await api_client.get("/backups")
    assert resp.status == 200
    body = await resp.json()
    assert body["data"]["backups"][0]["slug"] == "d9c48f8b"
    assert body["data"]["backups"][0]["location"] is None
    assert body["data"]["backups"][0]["locations"] == [None]
    assert body["data"]["backups"][0]["protected"] is True
    assert body["data"]["backups"][0]["location_attributes"] == {
        ".local": {
            "protected": True,
            "size_bytes": 10240,
        }
    }


@pytest.mark.parametrize(
    ("backup_type", "options"), [("full", {}), ("partial", {"folders": ["ssl"]})]
)
@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
async def test_protected_backup(
    api_client: TestClient, coresys: CoreSys, backup_type: str, options: dict[str, Any]
):
    """Test creating a protected backup."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    resp = await api_client.post(
        f"/backups/new/{backup_type}",
        json={"name": "test", "password": "test"} | options,
    )
    assert resp.status == 200
    body = await resp.json()
    assert (slug := body["data"]["slug"])

    resp = await api_client.get("/backups")
    assert resp.status == 200
    body = await resp.json()
    assert body["data"]["backups"][0]["slug"] == slug
    assert body["data"]["backups"][0]["location"] is None
    assert body["data"]["backups"][0]["locations"] == [None]
    assert body["data"]["backups"][0]["protected"] is True
    assert (
        body["data"]["backups"][0]["location_attributes"][".local"]["protected"] is True
    )
    # NOTE: It is not safe to check size exactly here, as order of keys in
    # `homeassistant.json` and potentially other random data (e.g. isntance UUID,
    # backup slug) does change the size of the backup (due to gzip).
    assert body["data"]["backups"][0]["location_attributes"][".local"]["size_bytes"] > 0

    resp = await api_client.get(f"/backups/{slug}/info")
    assert resp.status == 200
    body = await resp.json()
    assert body["data"]["location"] is None
    assert body["data"]["locations"] == [None]
    assert body["data"]["protected"] is True
    assert body["data"]["location_attributes"][".local"]["protected"] is True
    assert body["data"]["location_attributes"][".local"]["size_bytes"] > 0


@pytest.mark.usefixtures(
    "path_extern", "mount_propagation", "mock_is_mount", "tmp_supervisor_data"
)
async def test_upload_to_mount(api_client: TestClient, coresys: CoreSys):
    """Test uploading a backup to a specific mount."""
    await coresys.mounts.load()
    (coresys.config.path_mounts / "backup_test").mkdir()
    mount = Mount.from_dict(
        coresys,
        {
            "name": "backup_test",
            "type": "cifs",
            "usage": "backup",
            "server": "backup.local",
            "share": "backups",
        },
    )
    await coresys.mounts.create_mount(mount)

    # Capture our backup initially
    backup_file = get_fixture_path("backup_example.tar")
    backup = Backup(coresys, backup_file, "in", None)
    await backup.load()

    # Upload it and confirm it matches what we had
    with backup_file.open("rb") as file, MultipartWriter("form-data") as mp:
        mp.append(file)
        resp = await api_client.post(
            "/backups/new/upload?location=backup_test", data=mp
        )

    assert resp.status == 200
    body = await resp.json()
    assert body["data"]["slug"] == "7fed74c8"
    assert backup == coresys.backups.get("7fed74c8")


@pytest.mark.parametrize(
    ("method", "url_path", "body", "backup_file"),
    [
        (
            "delete",
            "/backups/7fed74c8",
            {"location": ".cloud_backup"},
            "backup_example.tar",
        ),
        (
            "post",
            "/backups/7fed74c8/restore/partial",
            {"location": ".cloud_backup", "folders": ["ssl"]},
            "backup_example.tar",
        ),
        (
            "get",
            "/backups/7fed74c8/download?location=.cloud_backup",
            None,
            "backup_example.tar",
        ),
        (
            "post",
            "/backups/93b462f8/restore/partial",
            {"location": ".cloud_backup", "folders": ["ssl"], "password": "bad"},
            "backup_example_enc.tar",
        ),
    ],
)
@pytest.mark.usefixtures("tmp_supervisor_data")
async def test_missing_file_removes_location_from_cache(
    api_client: TestClient,
    coresys: CoreSys,
    method: str,
    url_path: str,
    body: dict[str, Any] | None,
    backup_file: str,
    supervisor_internet: AsyncMock,
):
    """Test finding a missing file removes the location from cache."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    backup_file = get_fixture_path(backup_file)
    copy(backup_file, coresys.config.path_backup)
    bad_location = Path(copy(backup_file, coresys.config.path_core_backup))
    await coresys.backups.reload()
    assert len(coresys.backups.list_backups) == 1
    slug = list(coresys.backups.list_backups)[0].slug

    # After reload, remove one of the file and confirm we have an out of date cache
    bad_location.unlink()
    assert coresys.backups.get(slug).all_locations.keys() == {
        None,
        ".cloud_backup",
    }

    resp = await api_client.request(method, url_path, json=body)
    assert resp.status == 404

    # Wait for reload task to complete and confirm location is removed
    await asyncio.sleep(0.01)
    assert coresys.backups.get(slug).all_locations.keys() == {None}


@pytest.mark.parametrize(
    ("method", "url_path", "body", "backup_file"),
    [
        ("delete", "/backups/7fed74c8", {"location": ".local"}, "backup_example.tar"),
        (
            "post",
            "/backups/7fed74c8/restore/partial",
            {"location": ".local", "folders": ["ssl"]},
            "backup_example.tar",
        ),
        (
            "get",
            "/backups/7fed74c8/download?location=.local",
            None,
            "backup_example.tar",
        ),
        (
            "post",
            "/backups/93b462f8/restore/partial",
            {"location": ".local", "folders": ["ssl"], "password": "bad"},
            "backup_example_enc.tar",
        ),
    ],
)
@pytest.mark.usefixtures("tmp_supervisor_data")
async def test_missing_file_removes_backup_from_cache(
    api_client: TestClient,
    coresys: CoreSys,
    method: str,
    url_path: str,
    body: dict[str, Any] | None,
    backup_file: str,
    supervisor_internet: AsyncMock,
):
    """Test finding a missing file removes the backup from cache if its the only one."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    backup_file = get_fixture_path(backup_file)
    bad_location = Path(copy(backup_file, coresys.config.path_backup))
    await coresys.backups.reload()
    assert len(coresys.backups.list_backups) == 1
    slug = list(coresys.backups.list_backups)[0].slug

    # After reload, remove one of the file and confirm we have an out of date cache
    bad_location.unlink()
    assert coresys.backups.get(slug).all_locations.keys() == {None}

    resp = await api_client.request(method, url_path, json=body)
    assert resp.status == 404

    # Wait for reload task to complete and confirm backup is removed
    await asyncio.sleep(0.01)
    assert not coresys.backups.list_backups


@pytest.mark.usefixtures("tmp_supervisor_data")
async def test_immediate_list_after_missing_file_restore(
    api_client: TestClient,
    coresys: CoreSys,
    supervisor_internet: AsyncMock,
):
    """Test race with reload for missing file on restore does not error."""
    await coresys.core.set_state(CoreState.RUNNING)
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000

    backup_file = get_fixture_path("backup_example.tar")
    bad_location = Path(copy(backup_file, coresys.config.path_backup))
    # Copy a second backup in so there's something to reload later
    copy(get_fixture_path("backup_example_enc.tar"), coresys.config.path_backup)
    await coresys.backups.reload()

    # After reload, remove one of the file and confirm we have an out of date cache
    bad_location.unlink()
    assert coresys.backups.get("7fed74c8").all_locations.keys() == {None}

    event = asyncio.Event()
    orig_wait = asyncio.wait

    async def mock_wait(tasks: list[asyncio.Task], *args, **kwargs):
        """Mock for asyncio wait that allows force of race condition."""
        if tasks[0].get_coro().__qualname__.startswith("BackupManager.reload"):
            await event.wait()
        return await orig_wait(tasks, *args, **kwargs)

    with patch("supervisor.backups.manager.asyncio.wait", new=mock_wait):
        resp = await api_client.post(
            "/backups/7fed74c8/restore/partial",
            json={"location": ".local", "folders": ["ssl"]},
        )
        assert resp.status == 404

    await asyncio.sleep(0)
    resp = await api_client.get("/backups")
    assert resp.status == 200
    result = await resp.json()
    assert len(result["data"]["backups"]) == 2

    event.set()
    await asyncio.sleep(0.1)
    resp = await api_client.get("/backups")
    assert resp.status == 200
    result = await resp.json()
    assert len(result["data"]["backups"]) == 1
    assert result["data"]["backups"][0]["slug"] == "93b462f8"
