"""Test backups API."""

from unittest.mock import patch

from aiohttp.test_utils import TestClient

from supervisor.backups.backup import Backup
from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.mounts.mount import Mount


async def test_info(api_client, coresys: CoreSys, mock_full_backup: Backup):
    """Test info endpoint."""
    resp = await api_client.get("/backups/info")
    result = await resp.json()
    assert result["data"]["days_until_stale"] == 30
    assert len(result["data"]["backups"]) == 1
    assert result["data"]["backups"][0]["slug"] == "test"
    assert result["data"]["backups"][0]["content"]["homeassistant"] is True
    assert len(result["data"]["backups"][0]["content"]["addons"]) == 1
    assert result["data"]["backups"][0]["content"]["addons"][0] == "local_ssh"


async def test_list(api_client, coresys: CoreSys, mock_full_backup: Backup):
    """Test list endpoint."""
    resp = await api_client.get("/backups")
    result = await resp.json()
    assert len(result["data"]["backups"]) == 1
    assert result["data"]["backups"][0]["slug"] == "test"
    assert result["data"]["backups"][0]["content"]["homeassistant"] is True
    assert len(result["data"]["backups"][0]["content"]["addons"]) == 1
    assert result["data"]["backups"][0]["content"]["addons"][0] == "local_ssh"


async def test_options(api_client, coresys: CoreSys):
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


async def test_backup_to_mount(
    api_client: TestClient, coresys: CoreSys, tmp_supervisor_data, path_extern
):
    """Test making a backup to a backup mount."""
    await coresys.mounts.load()
    (mount_dir := coresys.config.path_mounts / "backup_test").mkdir()
    await coresys.mounts.create_mount(
        Mount.from_dict(
            coresys,
            {
                "name": "backup_test",
                "type": "cifs",
                "usage": "backup",
                "server": "backup.local",
                "share": "backups",
            },
        )
    )

    coresys.core.state = CoreState.RUNNING
    coresys.hardware.disk.get_disk_free_space = lambda x: 5000
    resp = await api_client.post(
        "/backups/new/full",
        json={
            "name": "Mount test",
            "location": "backup_test",
        },
    )
    result = await resp.json()
    assert result["result"] == "ok"
    slug = result["data"]["slug"]

    assert (mount_dir / f"{slug}.tar").exists()
