"""Test mounts API."""

from aiohttp.test_utils import TestClient
import pytest

from supervisor.coresys import CoreSys
from supervisor.mounts.mount import Mount

from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.systemd import Systemd as SystemdService


@pytest.fixture(name="mount")
async def fixture_mount(coresys: CoreSys, tmp_supervisor_data, path_extern) -> Mount:
    """Add an initial mount and load mounts."""
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
    coresys.mounts._mounts = {"backup_test": mount}  # pylint: disable=protected-access
    await coresys.mounts.load()
    yield mount


async def test_api_mounts_info(api_client: TestClient):
    """Test mounts info api."""
    resp = await api_client.get("/mounts")
    result = await resp.json()

    assert result["data"]["mounts"] == []


async def test_api_create_mount(
    api_client: TestClient, coresys: CoreSys, tmp_supervisor_data, path_extern
):
    """Test creating a mount via API."""
    resp = await api_client.post(
        "/mounts",
        json={
            "name": "backup_test",
            "type": "cifs",
            "usage": "backup",
            "server": "backup.local",
            "share": "backups",
        },
    )
    result = await resp.json()
    assert result["result"] == "ok"

    resp = await api_client.get("/mounts")
    result = await resp.json()

    assert result["data"]["mounts"] == [
        {
            "name": "backup_test",
            "type": "cifs",
            "usage": "backup",
            "server": "backup.local",
            "share": "backups",
            "state": "active",
        }
    ]
    coresys.mounts.save_data.assert_called_once()


async def test_api_create_error_mount_exists(api_client: TestClient, mount):
    """Test create mount API errors when mount exists."""
    resp = await api_client.post(
        "/mounts",
        json={
            "name": "backup_test",
            "type": "cifs",
            "usage": "backup",
            "server": "backup.local",
            "share": "backups",
        },
    )
    assert resp.status == 400
    result = await resp.json()
    assert result["result"] == "error"
    assert result["message"] == "A mount already exists with name backup_test"


async def test_api_update_mount(api_client: TestClient, coresys: CoreSys, mount):
    """Test updating a mount via API."""
    resp = await api_client.put(
        "/mounts/backup_test",
        json={
            "type": "cifs",
            "usage": "backup",
            "server": "backup.local",
            "share": "new_backups",
        },
    )
    result = await resp.json()
    assert result["result"] == "ok"

    resp = await api_client.get("/mounts")
    result = await resp.json()

    assert result["data"]["mounts"] == [
        {
            "name": "backup_test",
            "type": "cifs",
            "usage": "backup",
            "server": "backup.local",
            "share": "new_backups",
            "state": "active",
        }
    ]
    coresys.mounts.save_data.assert_called_once()


async def test_api_update_error_mount_missing(api_client: TestClient):
    """Test update mount API errors when mount does not exist."""
    resp = await api_client.put(
        "/mounts/backup_test",
        json={
            "type": "cifs",
            "usage": "backup",
            "server": "backup.local",
            "share": "new_backups",
        },
    )
    assert resp.status == 400
    result = await resp.json()
    assert result["result"] == "error"
    assert result["message"] == "No mount exists with name backup_test"


async def test_api_reload_mount(
    api_client: TestClient, all_dbus_services: dict[str, DBusServiceMock], mount
):
    """Test reloading a mount via API."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.ReloadOrRestartUnit.calls.clear()

    resp = await api_client.post("/mounts/backup_test/reload")
    result = await resp.json()
    assert result["result"] == "ok"

    assert systemd_service.ReloadOrRestartUnit.calls == [
        ("mnt-data-supervisor-mounts-backup_test.mount", "fail")
    ]


async def test_api_reload_error_mount_missing(api_client: TestClient):
    """Test reload mount API errors when mount does not exist."""
    resp = await api_client.post("/mounts/backup_test/reload")
    assert resp.status == 400
    result = await resp.json()
    assert result["result"] == "error"
    assert result["message"] == "No mount exists with name backup_test"


async def test_api_delete_mount(api_client: TestClient, coresys: CoreSys, mount):
    """Test deleting a mount via API."""
    resp = await api_client.delete("/mounts/backup_test")
    result = await resp.json()
    assert result["result"] == "ok"

    resp = await api_client.get("/mounts")
    result = await resp.json()

    assert result["data"]["mounts"] == []

    coresys.mounts.save_data.assert_called_once()


async def test_api_delete_error_mount_missing(api_client: TestClient):
    """Test delete mount API errors when mount does not exist."""
    resp = await api_client.delete("/mounts/backup_test")
    assert resp.status == 400
    result = await resp.json()
    assert result["result"] == "error"
    assert result["message"] == "No mount exists with name backup_test"
