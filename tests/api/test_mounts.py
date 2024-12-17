"""Test mounts API."""

import asyncio
from unittest.mock import patch

from aiohttp.test_utils import TestClient
from dbus_fast import DBusError, ErrorType
import pytest

from supervisor.backups.manager import BackupManager
from supervisor.coresys import CoreSys
from supervisor.mounts.mount import Mount

from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.systemd import Systemd as SystemdService
from tests.dbus_service_mocks.systemd_unit import SystemdUnit as SystemdUnitService


@pytest.fixture(name="mount")
async def fixture_mount(
    coresys: CoreSys, tmp_supervisor_data, path_extern, mount_propagation
) -> Mount:
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
    coresys.mounts.default_backup_mount = mount
    await coresys.mounts.load()
    yield mount


async def test_api_mounts_info(api_client: TestClient):
    """Test mounts info api."""
    resp = await api_client.get("/mounts")
    result = await resp.json()

    assert result["data"]["mounts"] == []


async def test_api_create_mount(
    api_client: TestClient,
    coresys: CoreSys,
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    mock_is_mount,
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
            "version": "2.0",
        },
    )
    result = await resp.json()
    assert result["result"] == "ok"

    resp = await api_client.get("/mounts")
    result = await resp.json()

    assert result["data"]["mounts"] == [
        {
            "version": "2.0",
            "name": "backup_test",
            "type": "cifs",
            "usage": "backup",
            "server": "backup.local",
            "share": "backups",
            "state": "active",
            "read_only": False,
            "user_path": None,
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


async def test_api_create_dbus_error_mount_not_added(
    api_client: TestClient,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
):
    """Test mount not added to list of mounts if a dbus error occurs."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_unit_service: SystemdUnitService = all_dbus_services["systemd_unit"]
    systemd_service.response_get_unit = DBusError(
        "org.freedesktop.systemd1.NoSuchUnit", "error"
    )
    systemd_service.response_start_transient_unit = DBusError(ErrorType.FAILED, "fail")

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
    assert result["message"] == "Could not mount backup_test due to: fail"

    resp = await api_client.get("/mounts")
    result = await resp.json()
    assert result["data"]["mounts"] == []

    systemd_service.response_get_unit = [
        DBusError("org.freedesktop.systemd1.NoSuchUnit", "error"),
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
    ]
    systemd_service.response_start_transient_unit = "/org/freedesktop/systemd1/job/7623"
    systemd_unit_service.active_state = ["failed", "failed", "inactive"]

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
    assert (
        result["message"]
        == "Mounting backup_test did not succeed. Check host logs for errors from mount or systemd unit mnt-data-supervisor-mounts-backup_test.mount for details."
    )

    resp = await api_client.get("/mounts")
    result = await resp.json()
    assert result["data"]["mounts"] == []


@pytest.mark.parametrize("os_available", ["9.5"], indirect=True)
async def test_api_create_mount_fails_os_out_of_date(
    api_client: TestClient,
    coresys: CoreSys,
    os_available,
    mount_propagation,
):
    """Test creating a mount via API fails when mounting isn't supported due to OS version."""
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
    assert (
        result["message"]
        == "'MountManager.create_mount' blocked from execution, mounting not supported on system"
    )


async def test_api_create_mount_fails_missing_mount_propagation(
    api_client: TestClient,
    coresys: CoreSys,
    os_available,
):
    """Test creating a mount via API fails when mounting isn't supported due to container config."""
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
    assert (
        result["message"]
        == "'MountManager.create_mount' blocked from execution, mounting not supported on system"
    )


async def test_api_update_mount(
    api_client: TestClient,
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    mount,
    mock_is_mount,
):
    """Test updating a mount via API."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_unit_service: SystemdUnitService = all_dbus_services["systemd_unit"]
    systemd_service.mock_systemd_unit = systemd_unit_service
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
            "version": None,
            "name": "backup_test",
            "type": "cifs",
            "usage": "backup",
            "server": "backup.local",
            "share": "new_backups",
            "state": "active",
            "read_only": False,
            "user_path": None,
        }
    ]
    coresys.mounts.save_data.assert_called_once()


async def test_api_update_dbus_error_mount_remains(
    api_client: TestClient,
    all_dbus_services: dict[str, DBusServiceMock],
    mount,
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
):
    """Test mount remains in list with unsuccessful state if dbus error occurs during update."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_unit_service: SystemdUnitService = all_dbus_services["systemd_unit"]
    systemd_unit_service.active_state = ["failed", "inactive"]
    systemd_service.response_get_unit = [
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        DBusError("org.freedesktop.systemd1.NoSuchUnit", "error"),
    ]
    systemd_service.response_start_transient_unit = DBusError(ErrorType.FAILED, "fail")

    resp = await api_client.put(
        "/mounts/backup_test",
        json={
            "type": "cifs",
            "usage": "backup",
            "server": "backup.local",
            "share": "backups1",
        },
    )
    assert resp.status == 400
    result = await resp.json()
    assert result["result"] == "error"
    assert result["message"] == "Could not mount backup_test due to: fail"

    resp = await api_client.get("/mounts")
    result = await resp.json()
    assert result["data"]["mounts"] == [
        {
            "version": None,
            "name": "backup_test",
            "type": "cifs",
            "usage": "backup",
            "server": "backup.local",
            "share": "backups",
            "state": None,
            "read_only": False,
            "user_path": None,
        }
    ]

    systemd_service.response_get_unit = [
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        DBusError("org.freedesktop.systemd1.NoSuchUnit", "error"),
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
    ]
    systemd_service.response_start_transient_unit = "/org/freedesktop/systemd1/job/7623"
    systemd_unit_service.active_state = [
        "failed",
        "inactive",
        "inactive",
        "failed",
        "inactive",
    ]

    resp = await api_client.put(
        "/mounts/backup_test",
        json={
            "type": "cifs",
            "usage": "backup",
            "server": "backup.local",
            "share": "backups2",
        },
    )
    assert resp.status == 400
    result = await resp.json()
    assert result["result"] == "error"
    assert (
        result["message"]
        == "Mounting backup_test did not succeed. Check host logs for errors from mount or systemd unit mnt-data-supervisor-mounts-backup_test.mount for details."
    )

    resp = await api_client.get("/mounts")
    result = await resp.json()
    assert result["data"]["mounts"] == [
        {
            "version": None,
            "name": "backup_test",
            "type": "cifs",
            "usage": "backup",
            "server": "backup.local",
            "share": "backups",
            "state": None,
            "read_only": False,
            "user_path": None,
        }
    ]


async def test_api_reload_mount(
    api_client: TestClient,
    all_dbus_services: dict[str, DBusServiceMock],
    mount,
    mock_is_mount,
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


async def test_api_delete_mount(
    api_client: TestClient,
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    mount,
):
    """Test deleting a mount via API."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_unit_service: SystemdUnitService = all_dbus_services["systemd_unit"]
    systemd_service.mock_systemd_unit = systemd_unit_service
    resp = await api_client.delete("/mounts/backup_test")
    result = await resp.json()
    assert result["result"] == "ok"

    resp = await api_client.get("/mounts")
    result = await resp.json()

    assert result["data"]["mounts"] == []

    coresys.mounts.save_data.assert_called_once()


async def test_api_create_backup_mount_sets_default(
    api_client: TestClient,
    coresys: CoreSys,
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    mock_is_mount,
):
    """Test creating backup mounts sets default if not set."""
    await coresys.mounts.load()
    assert coresys.mounts.default_backup_mount is None

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
    assert coresys.mounts.default_backup_mount.name == "backup_test"

    # Confirm the default does not change if mount created after its been set
    resp = await api_client.post(
        "/mounts",
        json={
            "name": "backup_test_2",
            "type": "cifs",
            "usage": "backup",
            "server": "backup.local",
            "share": "backups",
        },
    )
    result = await resp.json()
    assert result["result"] == "ok"
    assert coresys.mounts.default_backup_mount.name == "backup_test"


async def test_update_backup_mount_changes_default(
    api_client: TestClient,
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    mount,
    mock_is_mount,
):
    """Test updating a backup mount may unset the default."""
    systemd_unit_service: SystemdUnitService = all_dbus_services["systemd_unit"]
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.mock_systemd_unit = systemd_unit_service

    # Make another backup mount for testing
    resp = await api_client.post(
        "/mounts",
        json={
            "name": "other_backup_test",
            "type": "cifs",
            "usage": "backup",
            "server": "backup.local",
            "share": "backups",
        },
    )
    result = await resp.json()
    assert result["result"] == "ok"

    # Changing this mount should have no effect on the default
    resp = await api_client.put(
        "/mounts/other_backup_test",
        json={
            "type": "cifs",
            "usage": "media",
            "server": "other-media.local",
            "share": "media",
        },
    )
    result = await resp.json()
    assert result["result"] == "ok"
    assert coresys.mounts.default_backup_mount.name == "backup_test"

    # Changing this one to non-backup should unset the default
    resp = await api_client.put(
        "/mounts/backup_test",
        json={
            "type": "cifs",
            "usage": "media",
            "server": "media.local",
            "share": "media",
        },
    )
    result = await resp.json()
    assert result["result"] == "ok"
    assert coresys.mounts.default_backup_mount is None


async def test_delete_backup_mount_changes_default(
    api_client: TestClient,
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    mount,
    mock_is_mount,
):
    """Test deleting a backup mount may unset the default."""
    systemd_unit_service: SystemdUnitService = all_dbus_services["systemd_unit"]
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.mock_systemd_unit = systemd_unit_service

    # Make another backup mount for testing
    resp = await api_client.post(
        "/mounts",
        json={
            "name": "other_backup_test",
            "type": "cifs",
            "usage": "backup",
            "server": "backup.local",
            "share": "backups",
        },
    )
    result = await resp.json()
    assert result["result"] == "ok"

    # Deleting this one should have no effect on the default
    resp = await api_client.delete("/mounts/other_backup_test")
    result = await resp.json()
    assert result["result"] == "ok"
    assert coresys.mounts.default_backup_mount.name == "backup_test"

    # Deleting this current default should unset it
    resp = await api_client.delete("/mounts/backup_test")
    result = await resp.json()
    assert result["result"] == "ok"
    assert coresys.mounts.default_backup_mount is None


async def test_backup_mounts_reload_backups(
    api_client: TestClient,
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    mock_is_mount,
):
    """Test actions on a backup mount reload backups."""
    systemd_unit_service: SystemdUnitService = all_dbus_services["systemd_unit"]
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.mock_systemd_unit = systemd_unit_service
    await coresys.mounts.load()

    with patch.object(BackupManager, "reload") as reload:
        # Only creating a backup mount triggers reload
        resp = await api_client.post(
            "/mounts",
            json={
                "name": "media_test",
                "type": "cifs",
                "usage": "media",
                "server": "media.local",
                "share": "media",
            },
        )
        result = await resp.json()
        assert result["result"] == "ok"
        await asyncio.sleep(0)
        reload.assert_not_called()

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
        await asyncio.sleep(0)
        reload.assert_called_once()

        # Only updating a backup mount triggers reload
        reload.reset_mock()
        resp = await api_client.put(
            "/mounts/media_test",
            json={
                "type": "cifs",
                "usage": "media",
                "server": "media.local",
                "share": "media2",
            },
        )
        result = await resp.json()
        assert result["result"] == "ok"
        await asyncio.sleep(0)
        reload.assert_not_called()

        resp = await api_client.put(
            "/mounts/backup_test",
            json={
                "type": "cifs",
                "usage": "backup",
                "server": "backup.local",
                "share": "backups2",
            },
        )
        result = await resp.json()
        assert result["result"] == "ok"
        await asyncio.sleep(0)
        reload.assert_called_once()

        # Only reloading a backup mount triggers reload
        reload.reset_mock()
        resp = await api_client.post("/mounts/media_test/reload")
        result = await resp.json()
        assert result["result"] == "ok"
        await asyncio.sleep(0)
        reload.assert_not_called()

        resp = await api_client.post("/mounts/backup_test/reload")
        result = await resp.json()
        assert result["result"] == "ok"
        await asyncio.sleep(0)
        reload.assert_called_once()

        # Only deleting a backup mount triggers reload
        reload.reset_mock()
        resp = await api_client.delete("/mounts/media_test")
        result = await resp.json()
        assert result["result"] == "ok"
        await asyncio.sleep(0)
        reload.assert_not_called()

        resp = await api_client.delete("/mounts/backup_test")
        result = await resp.json()
        assert result["result"] == "ok"
        await asyncio.sleep(0)
        reload.assert_called_once()


async def test_options(api_client: TestClient, coresys: CoreSys, mount, mock_is_mount):
    """Test changing options."""
    resp = await api_client.post(
        "/mounts",
        json={
            "name": "other_backup_test",
            "type": "cifs",
            "usage": "backup",
            "server": "backup.local",
            "share": "backups",
        },
    )
    result = await resp.json()
    assert result["result"] == "ok"

    resp = await api_client.post(
        "/mounts",
        json={
            "name": "media_test",
            "type": "cifs",
            "usage": "media",
            "server": "media.local",
            "share": "media",
        },
    )
    result = await resp.json()
    assert result["result"] == "ok"

    coresys.mounts.save_data.reset_mock()

    # Not a backup mount, will fail
    resp = await api_client.post(
        "/mounts/options",
        json={
            "default_backup_mount": "media_test",
        },
    )
    result = await resp.json()
    assert result["result"] == "error"

    # Mount doesn't exist, will fail
    resp = await api_client.post(
        "/mounts/options",
        json={
            "default_backup_mount": "junk",
        },
    )
    result = await resp.json()
    assert result["result"] == "error"

    assert coresys.mounts.default_backup_mount.name == "backup_test"
    coresys.mounts.save_data.assert_not_called()

    # Changes to new backup mount
    resp = await api_client.post(
        "/mounts/options",
        json={
            "default_backup_mount": "other_backup_test",
        },
    )
    result = await resp.json()
    assert result["result"] == "ok"

    assert coresys.mounts.default_backup_mount.name == "other_backup_test"
    coresys.mounts.save_data.assert_called_once()

    # Unsets default backup mount
    resp = await api_client.post(
        "/mounts/options",
        json={
            "default_backup_mount": None,
        },
    )
    result = await resp.json()
    assert result["result"] == "ok"

    assert coresys.mounts.default_backup_mount is None
    assert coresys.mounts.save_data.call_count == 2


async def test_api_create_mount_fails_special_chars(
    api_client: TestClient,
    coresys: CoreSys,
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
):
    """Test creating a mount via API fails with special characters."""
    resp = await api_client.post(
        "/mounts",
        json={
            "name": "Überwachungskameras",
            "type": "cifs",
            "usage": "backup",
            "server": "backup.local",
            "share": "backups",
            "version": "2.0",
        },
    )
    result = await resp.json()
    assert result["result"] == "error"
    assert "does not match regular expression" in result["message"]


async def test_api_create_read_only_cifs_mount(
    api_client: TestClient,
    coresys: CoreSys,
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    mock_is_mount,
):
    """Test creating a read-only cifs mount via API."""
    resp = await api_client.post(
        "/mounts",
        json={
            "name": "media_test",
            "type": "cifs",
            "usage": "media",
            "server": "media.local",
            "share": "media",
            "version": "2.0",
            "read_only": True,
        },
    )
    result = await resp.json()
    assert result["result"] == "ok"

    resp = await api_client.get("/mounts")
    result = await resp.json()

    assert result["data"]["mounts"] == [
        {
            "version": "2.0",
            "name": "media_test",
            "type": "cifs",
            "usage": "media",
            "server": "media.local",
            "share": "media",
            "state": "active",
            "read_only": True,
            "user_path": "/media/media_test",
        }
    ]
    coresys.mounts.save_data.assert_called_once()


async def test_api_create_read_only_nfs_mount(
    api_client: TestClient,
    coresys: CoreSys,
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    mock_is_mount,
):
    """Test creating a read-only nfs mount via API."""
    resp = await api_client.post(
        "/mounts",
        json={
            "name": "media_test",
            "type": "nfs",
            "usage": "media",
            "server": "media.local",
            "path": "/media/camera",
            "read_only": True,
        },
    )
    result = await resp.json()
    assert result["result"] == "ok"

    resp = await api_client.get("/mounts")
    result = await resp.json()

    assert result["data"]["mounts"] == [
        {
            "name": "media_test",
            "type": "nfs",
            "usage": "media",
            "server": "media.local",
            "path": "/media/camera",
            "state": "active",
            "read_only": True,
            "user_path": "/media/media_test",
        }
    ]
    coresys.mounts.save_data.assert_called_once()


async def test_api_read_only_backup_mount_invalid(
    api_client: TestClient,
    coresys: CoreSys,
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
):
    """Test cannot create a read-only backup mount."""
    resp = await api_client.post(
        "/mounts",
        json={
            "name": "backup_test",
            "type": "cifs",
            "usage": "backup",
            "server": "backup.local",
            "share": "backup",
            "version": "2.0",
            "read_only": True,
        },
    )
    assert resp.status == 400
    result = await resp.json()
    assert result["result"] == "error"
    assert "Backup mounts cannot be read only" in result["message"]


@pytest.mark.parametrize(
    ("method", "url"),
    [
        ("put", "/mounts/bad"),
        ("delete", "/mounts/bad"),
        ("post", "/mounts/bad/reload"),
    ],
)
async def test_mount_not_found(api_client: TestClient, method: str, url: str):
    """Test mount not found error."""
    resp = await api_client.request(method, url)
    assert resp.status == 404
    resp = await resp.json()
    assert resp["message"] == "No mount exists with name bad"
