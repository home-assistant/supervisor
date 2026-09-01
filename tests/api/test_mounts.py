"""Test mounts API."""

import asyncio
from dataclasses import replace
import errno
from unittest.mock import PropertyMock, patch

from aiohttp.test_utils import TestClient
from dbus_fast import DBusError, ErrorType
import pytest

from supervisor.backups.manager import BackupManager
from supervisor.coresys import CoreSys
from supervisor.exceptions import DBusObjectError
from supervisor.mounts.mount import Mount

from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.systemd import Systemd as SystemdService
from tests.dbus_service_mocks.systemd_unit import SystemdUnit as SystemdUnitService
from tests.dbus_service_mocks.udisks2_manager import (
    UDisks2Manager as UDisks2ManagerService,
)

SDC1_OBJECT_PATH = "/org/freedesktop/UDisks2/block_devices/sdc1"
SDC1_UUID = "d2f4a6c8-3b5e-4079-8a1c-6e9d2f4b7a30"


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
    return mount


async def test_api_mounts_info(api_client_with_prefix: tuple[TestClient, str]):
    """Test mounts info api."""
    api_client, prefix = api_client_with_prefix
    resp = await api_client.get(f"{prefix}/mounts")
    result = await resp.json()

    assert result["data"]["mounts"] == []


async def test_api_create_mount(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    mock_is_mount,
):
    """Test creating a mount via API."""
    api_client, prefix = api_client_with_prefix
    resp = await api_client.post(
        f"{prefix}/mounts",
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

    resp = await api_client.get(f"{prefix}/mounts")
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


async def test_api_create_error_mount_exists(
    api_client_with_prefix: tuple[TestClient, str], mount
):
    """Test create mount API errors when mount exists."""
    api_client, prefix = api_client_with_prefix
    resp = await api_client.post(
        f"{prefix}/mounts",
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
    api_client_with_prefix: tuple[TestClient, str],
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    caplog: pytest.LogCaptureFixture,
):
    """Test mount not added to list of mounts if a dbus error occurs."""
    api_client, prefix = api_client_with_prefix
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_unit_service: SystemdUnitService = all_dbus_services["systemd_unit"]
    systemd_service.response_get_unit = DBusError(
        "org.freedesktop.systemd1.NoSuchUnit", "error"
    )
    systemd_service.response_start_transient_unit = DBusError(ErrorType.FAILED, "fail")

    # Mount failures reflect host/config conditions, not Supervisor bugs, so they
    # must be reported as client-side errors without capturing to Sentry.
    with patch("supervisor.api.utils.async_capture_exception") as capture_exception:
        resp = await api_client.post(
            f"{prefix}/mounts",
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
        # User-facing message is generic and translatable...
        assert (
            result["message"]
            == "Could not set up mount backup_test. Check the Supervisor logs for details"
        )
        assert result["error_key"] == "mount_setup_error"
        assert result["extra_fields"] == {"name": "backup_test"}
        capture_exception.assert_not_called()

    # ...while the D-Bus detail is only in the log
    assert "Could not mount backup_test due to: fail" in caplog.text

    resp = await api_client.get(f"{prefix}/mounts")
    result = await resp.json()
    assert result["data"]["mounts"] == []

    caplog.clear()
    systemd_service.response_get_unit = [
        DBusError("org.freedesktop.systemd1.NoSuchUnit", "error"),
        DBusError("org.freedesktop.systemd1.NoSuchUnit", "error"),
        DBusError("org.freedesktop.systemd1.NoSuchUnit", "error"),
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
    ]
    systemd_service.response_start_transient_unit = "/org/freedesktop/systemd1/job/7623"
    systemd_unit_service.active_state = ["failed", "failed"]

    with patch("supervisor.api.utils.async_capture_exception") as capture_exception:
        resp = await api_client.post(
            f"{prefix}/mounts",
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
            == "Mount backup_test is not reachable. Check the Supervisor logs for details"
        )
        assert result["error_key"] == "mount_activation_error"
        assert result["extra_fields"] == {"name": "backup_test"}
        capture_exception.assert_not_called()

    assert (
        "Mounting backup_test did not succeed. Check host logs for errors from mount "
        "or systemd unit mnt-data-supervisor-mounts-backup_test.mount for details"
    ) in caplog.text

    resp = await api_client.get(f"{prefix}/mounts")
    result = await resp.json()
    assert result["data"]["mounts"] == []


@pytest.mark.parametrize("os_available", ["9.5"], indirect=True)
async def test_api_create_mount_fails_os_out_of_date(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    os_available,
    mount_propagation,
):
    """Test creating a mount via API fails when mounting isn't supported due to OS version."""
    api_client, prefix = api_client_with_prefix
    resp = await api_client.post(
        f"{prefix}/mounts",
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
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    os_available,
):
    """Test creating a mount via API fails when mounting isn't supported due to container config."""
    api_client, prefix = api_client_with_prefix
    resp = await api_client.post(
        f"{prefix}/mounts",
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
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    mount,
    mock_is_mount,
):
    """Test updating a mount via API."""
    api_client, prefix = api_client_with_prefix
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_unit_service: SystemdUnitService = all_dbus_services["systemd_unit"]
    systemd_service.mock_systemd_unit = systemd_unit_service
    resp = await api_client.put(
        f"{prefix}/mounts/backup_test",
        json={
            "type": "cifs",
            "usage": "backup",
            "server": "backup.local",
            "share": "new_backups",
        },
    )
    result = await resp.json()
    assert result["result"] == "ok"

    resp = await api_client.get(f"{prefix}/mounts")
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
    api_client_with_prefix: tuple[TestClient, str],
    all_dbus_services: dict[str, DBusServiceMock],
    mount,
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    caplog: pytest.LogCaptureFixture,
):
    """Test mount remains in list with unsuccessful state if dbus error occurs during update."""
    api_client, prefix = api_client_with_prefix
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_unit_service: SystemdUnitService = all_dbus_services["systemd_unit"]
    systemd_unit_service.active_state = ["failed", "inactive"]
    # Sequence: old-mount unmount lookup, then .mount/.automount/legacy
    # lookups of the fresh setup (all gone after the unmount).
    systemd_service.response_get_unit = [
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        DBusError("org.freedesktop.systemd1.NoSuchUnit", "error"),
        DBusError("org.freedesktop.systemd1.NoSuchUnit", "error"),
        DBusError("org.freedesktop.systemd1.NoSuchUnit", "error"),
    ]
    systemd_service.response_start_transient_unit = DBusError(ErrorType.FAILED, "fail")

    resp = await api_client.put(
        f"{prefix}/mounts/backup_test",
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
    # User-facing message is generic and translatable, detail stays in the log
    assert (
        result["message"]
        == "Could not set up mount backup_test. Check the Supervisor logs for details"
    )
    assert result["error_key"] == "mount_setup_error"
    assert result["extra_fields"] == {"name": "backup_test"}
    assert "Could not mount backup_test due to: fail" in caplog.text

    resp = await api_client.get(f"{prefix}/mounts")
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
        DBusError("org.freedesktop.systemd1.NoSuchUnit", "error"),
        DBusError("org.freedesktop.systemd1.NoSuchUnit", "error"),
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
    ]
    systemd_service.response_start_transient_unit = "/org/freedesktop/systemd1/job/7623"
    systemd_unit_service.active_state = [
        "failed",
        "failed",
        "failed",
    ]
    caplog.clear()

    resp = await api_client.put(
        f"{prefix}/mounts/backup_test",
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
        == "Mount backup_test is not reachable. Check the Supervisor logs for details"
    )
    assert result["error_key"] == "mount_activation_error"
    assert result["extra_fields"] == {"name": "backup_test"}
    assert (
        "Mounting backup_test did not succeed. Check host logs for errors from mount "
        "or systemd unit mnt-data-supervisor-mounts-backup_test.mount for details"
    ) in caplog.text

    resp = await api_client.get(f"{prefix}/mounts")
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
    api_client_with_prefix: tuple[TestClient, str],
    all_dbus_services: dict[str, DBusServiceMock],
    mount,
    mock_is_mount,
):
    """Test reloading a mount via API.

    With autofs handling re-activation, "reload" reduces to a probe of the
    mount's health. Neither a healthy nor an unreachable mount is reloaded
    or restarted through systemd.
    """
    api_client, prefix = api_client_with_prefix
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.ReloadOrRestartUnit.calls.clear()

    # Healthy mount (probe passes): API reload returns ok and dismisses
    # any failed-mount resolution issue.
    resp = await api_client.post(f"{prefix}/mounts/backup_test/reload")
    result = await resp.json()
    assert result["result"] == "ok"
    assert systemd_service.ReloadOrRestartUnit.calls == []

    # Probe failure: API reload returns an error response. The escalation
    # stops the .mount unit to discard the dead session, but never
    # reloads or restarts it.
    with patch(
        "supervisor.mounts.mount._probe_mount",
        side_effect=OSError(errno.EHOSTDOWN, "Host is down"),
    ):
        resp = await api_client.post(f"{prefix}/mounts/backup_test/reload")
        result = await resp.json()
    assert result["result"] == "error"
    assert systemd_service.ReloadOrRestartUnit.calls == []


async def test_api_delete_mount(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    mount,
):
    """Test deleting a mount via API."""
    api_client, prefix = api_client_with_prefix
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_unit_service: SystemdUnitService = all_dbus_services["systemd_unit"]
    systemd_service.mock_systemd_unit = systemd_unit_service
    resp = await api_client.delete(f"{prefix}/mounts/backup_test")
    result = await resp.json()
    assert result["result"] == "ok"

    resp = await api_client.get(f"{prefix}/mounts")
    result = await resp.json()

    assert result["data"]["mounts"] == []

    coresys.mounts.save_data.assert_called_once()


async def test_api_create_backup_mount_sets_default(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    mock_is_mount,
):
    """Test creating backup mounts sets default if not set."""
    api_client, prefix = api_client_with_prefix
    await coresys.mounts.load()
    assert coresys.mounts.default_backup_mount is None

    resp = await api_client.post(
        f"{prefix}/mounts",
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
        f"{prefix}/mounts",
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
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    mount,
    mock_is_mount,
):
    """Test updating a backup mount may unset the default."""
    api_client, prefix = api_client_with_prefix
    systemd_unit_service: SystemdUnitService = all_dbus_services["systemd_unit"]
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.mock_systemd_unit = systemd_unit_service

    # Make another backup mount for testing
    resp = await api_client.post(
        f"{prefix}/mounts",
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
        f"{prefix}/mounts/other_backup_test",
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
        f"{prefix}/mounts/backup_test",
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
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    mount,
    mock_is_mount,
):
    """Test deleting a backup mount may unset the default."""
    api_client, prefix = api_client_with_prefix
    systemd_unit_service: SystemdUnitService = all_dbus_services["systemd_unit"]
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.mock_systemd_unit = systemd_unit_service

    # Make another backup mount for testing
    resp = await api_client.post(
        f"{prefix}/mounts",
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
    resp = await api_client.delete(f"{prefix}/mounts/other_backup_test")
    result = await resp.json()
    assert result["result"] == "ok"
    assert coresys.mounts.default_backup_mount.name == "backup_test"

    # Deleting this current default should unset it
    resp = await api_client.delete(f"{prefix}/mounts/backup_test")
    result = await resp.json()
    assert result["result"] == "ok"
    assert coresys.mounts.default_backup_mount is None


async def test_backup_mounts_reload_backups(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    mock_is_mount,
):
    """Test actions on a backup mount reload backups."""
    api_client, prefix = api_client_with_prefix
    systemd_unit_service: SystemdUnitService = all_dbus_services["systemd_unit"]
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.mock_systemd_unit = systemd_unit_service
    await coresys.mounts.load()

    with patch.object(BackupManager, "reload") as reload:
        # Only creating a backup mount triggers reload
        resp = await api_client.post(
            f"{prefix}/mounts",
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
            f"{prefix}/mounts",
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
            f"{prefix}/mounts/media_test",
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
            f"{prefix}/mounts/backup_test",
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
        resp = await api_client.post(f"{prefix}/mounts/media_test/reload")
        result = await resp.json()
        assert result["result"] == "ok"
        await asyncio.sleep(0)
        reload.assert_not_called()

        resp = await api_client.post(f"{prefix}/mounts/backup_test/reload")
        result = await resp.json()
        assert result["result"] == "ok"
        await asyncio.sleep(0)
        reload.assert_called_once()

        # Only deleting a backup mount triggers reload
        reload.reset_mock()
        resp = await api_client.delete(f"{prefix}/mounts/media_test")
        result = await resp.json()
        assert result["result"] == "ok"
        await asyncio.sleep(0)
        reload.assert_not_called()

        resp = await api_client.delete(f"{prefix}/mounts/backup_test")
        result = await resp.json()
        assert result["result"] == "ok"
        await asyncio.sleep(0)
        reload.assert_called_once()


async def test_options(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    mount,
    mock_is_mount,
):
    """Test changing options."""
    api_client, prefix = api_client_with_prefix
    resp = await api_client.post(
        f"{prefix}/mounts",
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
        f"{prefix}/mounts",
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
        f"{prefix}/mounts/options",
        json={
            "default_backup_mount": "media_test",
        },
    )
    result = await resp.json()
    assert result["result"] == "error"

    # Mount doesn't exist, will fail
    resp = await api_client.post(
        f"{prefix}/mounts/options",
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
        f"{prefix}/mounts/options",
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
        f"{prefix}/mounts/options",
        json={
            "default_backup_mount": None,
        },
    )
    result = await resp.json()
    assert result["result"] == "ok"

    assert coresys.mounts.default_backup_mount is None
    assert coresys.mounts.save_data.call_count == 2


async def test_api_create_mount_fails_special_chars(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
):
    """Test creating a mount via API fails with special characters."""
    api_client, prefix = api_client_with_prefix
    resp = await api_client.post(
        f"{prefix}/mounts",
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
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    mock_is_mount,
):
    """Test creating a read-only cifs mount via API."""
    api_client, prefix = api_client_with_prefix
    resp = await api_client.post(
        f"{prefix}/mounts",
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

    resp = await api_client.get(f"{prefix}/mounts")
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
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    mock_is_mount,
):
    """Test creating a read-only nfs mount via API."""
    api_client, prefix = api_client_with_prefix
    resp = await api_client.post(
        f"{prefix}/mounts",
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

    resp = await api_client.get(f"{prefix}/mounts")
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
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
):
    """Test cannot create a read-only backup mount."""
    api_client, prefix = api_client_with_prefix
    resp = await api_client.post(
        f"{prefix}/mounts",
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
async def test_mount_not_found(
    api_client_with_prefix: tuple[TestClient, str], method: str, url: str
):
    """Test mount not found error."""
    api_client, prefix = api_client_with_prefix
    resp = await api_client.request(method, f"{prefix}{url}")
    assert resp.status == 404
    resp = await resp.json()
    assert resp["message"] == "No mount exists with name bad"


async def test_api_mounts_candidates(
    api_client_with_prefix: tuple[TestClient, str],
    all_dbus_services: dict[str, DBusServiceMock],
    sdc_candidate: DBusServiceMock,
):
    """Test only the unmounted user disk is offered as a mount candidate.

    Every other block device on the mock host is excluded for its own
    reason: no filesystem (loop0, mmcblk1, mmcblk1p2, sda, sdb, sdc, zram1),
    hinted as a system device (mmcblk1p1, mmcblk1p3), labelled as a previous
    data disk (sda1), or already mounted (sdb1).
    """
    api_client, prefix = api_client_with_prefix
    udisks2_manager_service: UDisks2ManagerService = all_dbus_services[
        "udisks2_manager"
    ]
    udisks2_manager_service.GetBlockDevices.calls.clear()

    resp = await api_client.get(f"{prefix}/mounts/candidates")
    result = await resp.json()

    assert result["result"] == "ok"
    # Re-read from the host first, so a disk plugged in moments ago shows up
    assert len(udisks2_manager_service.GetBlockDevices.calls) == 1

    assert result["data"]["candidates"] == [
        {
            "type": "disk",
            "device": "/dev/sdc1",
            "uuid": SDC1_UUID,
            "label": "Backups",
            "filesystem": "ext4",
            "size": 2000397795328,
            "read_only": False,
            "drive": {
                "vendor": "Seagate",
                "model": "Expansion",
                "serial": "1234567890",
                "id": "Seagate-Expansion-1234567890",
                "size": 2000398934016,
                "connection_bus": "usb",
                "removable": True,
                "ejectable": True,
            },
        }
    ]


async def test_api_candidates_entry_posts_back_as_mount(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    sdc_candidate: DBusServiceMock,
    mock_is_mount,
):
    """Test a candidates entry plus a name is directly accepted by POST /mounts.

    The entry carries type, device, uuid and more; extra fields are dropped,
    both identifiers are accepted together, and resolution goes by uuid.
    """
    api_client, prefix = api_client_with_prefix
    udisks2_manager_service: UDisks2ManagerService = all_dbus_services[
        "udisks2_manager"
    ]
    udisks2_manager_service.resolved_devices = [SDC1_OBJECT_PATH]

    resp = await api_client.get(f"{prefix}/mounts/candidates")
    candidate = (await resp.json())["data"]["candidates"][0]

    resp = await api_client.post(
        f"{prefix}/mounts",
        json=candidate | {"name": "media_test", "usage": "media"},
    )
    result = await resp.json()
    assert result["result"] == "ok"

    resp = await api_client.get(f"{prefix}/mounts")
    result = await resp.json()
    assert result["data"]["mounts"] == [
        {
            "name": "media_test",
            "type": "disk",
            "usage": "media",
            "uuid": SDC1_UUID,
            "filesystem": "ext4",
            "state": "active",
            "read_only": False,
            "user_path": "/media/media_test",
        }
    ]


async def test_api_create_disk_mount_device_uuid_mismatch(
    api_client_with_prefix: tuple[TestClient, str],
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    sdc_candidate: DBusServiceMock,
):
    """Test disagreeing identifiers are refused, not silently resolved.

    Resolution goes by uuid; a device supplied alongside that no longer
    carries that uuid means the caller is working from stale information.
    """
    api_client, prefix = api_client_with_prefix
    udisks2_manager_service: UDisks2ManagerService = all_dbus_services[
        "udisks2_manager"
    ]
    # uuid resolves to sdc1, but the caller claims it lives at sdb1
    udisks2_manager_service.resolved_devices = [SDC1_OBJECT_PATH]

    resp = await api_client.post(
        f"{prefix}/mounts",
        json={
            "name": "media_test",
            "type": "disk",
            "usage": "media",
            "device": "/dev/sdb1",
            "uuid": SDC1_UUID,
        },
    )

    assert resp.status == 400
    result = await resp.json()
    assert result["error_key"] == "mount_device_mismatch_error"
    assert result["extra_fields"] == {"device": "/dev/sdb1", "uuid": SDC1_UUID}

    resp = await api_client.get(f"{prefix}/mounts")
    result = await resp.json()
    assert result["data"]["mounts"] == []


async def test_api_mounts_candidates_without_udisks2(
    api_client_with_prefix: tuple[TestClient, str], coresys: CoreSys
):
    """Test candidates come back empty, not as an error, without UDisks2.

    A supervised install may have no UDisks2 at all. There is then nothing to
    offer, which is an answer rather than a failure.
    """
    api_client, prefix = api_client_with_prefix

    with patch.object(
        type(coresys.dbus.udisks2),
        "is_connected",
        new_callable=PropertyMock,
        return_value=False,
    ):
        resp = await api_client.get(f"{prefix}/mounts/candidates")
        result = await resp.json()

    assert result["result"] == "ok"
    assert result["data"]["candidates"] == []


async def test_api_mounts_candidates_drive_lookup_fails(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    sdc_candidate: DBusServiceMock,
):
    """Test a candidate is still listed when its drive cannot be read.

    The drive object can vanish between enumeration and lookup if the disk is
    unplugged mid-request, which must not fail the whole listing.
    """
    api_client, prefix = api_client_with_prefix

    with patch.object(
        coresys.dbus.udisks2, "get_drive", side_effect=DBusObjectError("gone")
    ):
        resp = await api_client.get(f"{prefix}/mounts/candidates")
        result = await resp.json()

    assert result["result"] == "ok"
    assert len(result["data"]["candidates"]) == 1
    assert result["data"]["candidates"][0]["device"] == "/dev/sdc1"
    assert result["data"]["candidates"][0]["drive"] is None


async def test_api_mounts_candidates_without_drive(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    sdc_candidate: DBusServiceMock,
):
    """Test a candidate with no backing drive object reports a null drive."""
    api_client, prefix = api_client_with_prefix
    sdc_candidate.fixture = replace(sdc_candidate.fixture, Drive="/")
    await coresys.dbus.udisks2.update()

    resp = await api_client.get(f"{prefix}/mounts/candidates")
    result = await resp.json()

    assert result["result"] == "ok"
    assert len(result["data"]["candidates"]) == 1
    assert result["data"]["candidates"][0]["device"] == "/dev/sdc1"
    assert result["data"]["candidates"][0]["drive"] is None


async def test_api_create_disk_mount_by_device(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    sdc_candidate: DBusServiceMock,
    mock_is_mount,
):
    """Test creating a disk mount by device path via API."""
    api_client, prefix = api_client_with_prefix
    udisks2_manager_service: UDisks2ManagerService = all_dbus_services[
        "udisks2_manager"
    ]
    udisks2_manager_service.resolved_devices = [SDC1_OBJECT_PATH]

    resp = await api_client.post(
        f"{prefix}/mounts",
        json={
            "name": "media_test",
            "type": "disk",
            "usage": "media",
            "device": "/dev/sdc1",
        },
    )
    result = await resp.json()
    assert result["result"] == "ok"

    resp = await api_client.get(f"{prefix}/mounts")
    result = await resp.json()

    # The device path was only ever an input: what comes back is the stable
    # pair the mount is actually persisted and re-mounted by.
    assert result["data"]["mounts"] == [
        {
            "name": "media_test",
            "type": "disk",
            "usage": "media",
            "uuid": SDC1_UUID,
            "filesystem": "ext4",
            "state": "active",
            "read_only": False,
            "user_path": "/media/media_test",
        }
    ]
    coresys.mounts.save_data.assert_called_once()


async def test_api_create_disk_mount_by_uuid(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    sdc_candidate: DBusServiceMock,
    mock_is_mount,
):
    """Test creating a disk mount by filesystem UUID via API."""
    api_client, prefix = api_client_with_prefix
    udisks2_manager_service: UDisks2ManagerService = all_dbus_services[
        "udisks2_manager"
    ]
    udisks2_manager_service.resolved_devices = [SDC1_OBJECT_PATH]

    resp = await api_client.post(
        f"{prefix}/mounts",
        json={
            "name": "backup_test",
            "type": "disk",
            "usage": "backup",
            "uuid": SDC1_UUID,
        },
    )
    result = await resp.json()
    assert result["result"] == "ok"

    resp = await api_client.get(f"{prefix}/mounts")
    result = await resp.json()

    assert result["data"]["mounts"] == [
        {
            "name": "backup_test",
            "type": "disk",
            "usage": "backup",
            "uuid": SDC1_UUID,
            "filesystem": "ext4",
            "state": "active",
            "read_only": False,
            "user_path": None,
        }
    ]
    coresys.mounts.save_data.assert_called_once()


async def test_api_create_disk_mount_device_missing(
    api_client_with_prefix: tuple[TestClient, str],
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
):
    """Test creating a disk mount for a device that is not present."""
    api_client, prefix = api_client_with_prefix
    udisks2_manager_service: UDisks2ManagerService = all_dbus_services[
        "udisks2_manager"
    ]
    udisks2_manager_service.resolved_devices = []

    resp = await api_client.post(
        f"{prefix}/mounts",
        json={
            "name": "media_test",
            "type": "disk",
            "usage": "media",
            "device": "/dev/sdz9",
        },
    )

    assert resp.status == 400
    result = await resp.json()
    assert result["result"] == "error"
    assert result["message"] == "No disk found matching /dev/sdz9"
    assert result["error_key"] == "mount_device_not_found_error"
    assert result["extra_fields"] == {"reference": "/dev/sdz9"}

    resp = await api_client.get(f"{prefix}/mounts")
    result = await resp.json()
    assert result["data"]["mounts"] == []


async def test_api_create_disk_mount_cannot_skip_guards_with_filesystem(
    api_client_with_prefix: tuple[TestClient, str],
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
):
    """Test a caller cannot skip the guards by supplying filesystem themselves.

    Resolution is what runs the guard. If an API caller could pin `filesystem`,
    resolution would be skipped and every rail reduced to a hint for the picker
    UI — letting the OS data disk be mounted into /media.
    """
    api_client, prefix = api_client_with_prefix
    udisks2_manager_service: UDisks2ManagerService = all_dbus_services[
        "udisks2_manager"
    ]
    udisks2_manager_service.resolved_devices = [
        "/org/freedesktop/UDisks2/block_devices/sda1"
    ]

    resp = await api_client.post(
        f"{prefix}/mounts",
        json={
            "name": "media_test",
            "type": "disk",
            "usage": "media",
            # sda1 is hassos-data-old, excluded by the label rail
            "uuid": "b82b23cb-0c47-4bbb-acf5-2a2afa8894a2",
            "filesystem": "ext4",
        },
    )

    assert resp.status == 400
    result = await resp.json()
    assert result["result"] == "error"
    assert result["error_key"] == "mount_device_protected_error"

    resp = await api_client.get(f"{prefix}/mounts")
    result = await resp.json()
    assert result["data"]["mounts"] == []


async def test_api_update_disk_mount_cannot_skip_guards_with_filesystem(
    api_client_with_prefix: tuple[TestClient, str],
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    sdc_candidate: DBusServiceMock,
    mock_is_mount,
):
    """Test the update path runs the guard too, not only create."""
    api_client, prefix = api_client_with_prefix
    udisks2_manager_service: UDisks2ManagerService = all_dbus_services[
        "udisks2_manager"
    ]
    udisks2_manager_service.resolved_devices = [SDC1_OBJECT_PATH]

    resp = await api_client.post(
        f"{prefix}/mounts",
        json={
            "name": "media_test",
            "type": "disk",
            "usage": "media",
            "device": "/dev/sdc1",
        },
    )
    assert (await resp.json())["result"] == "ok"

    # Now try to repoint that mount at the OS data disk with a pinned filesystem
    udisks2_manager_service.resolved_devices = [
        "/org/freedesktop/UDisks2/block_devices/sda1"
    ]
    resp = await api_client.put(
        f"{prefix}/mounts/media_test",
        json={
            "type": "disk",
            "usage": "media",
            "uuid": "b82b23cb-0c47-4bbb-acf5-2a2afa8894a2",
            "filesystem": "ext4",
        },
    )

    assert resp.status == 400
    result = await resp.json()
    assert result["result"] == "error"
    assert result["error_key"] == "mount_device_protected_error"

    # Still pointing at the user's own disk, not repointed at the data disk
    resp = await api_client.get(f"{prefix}/mounts")
    mounts = (await resp.json())["data"]["mounts"]
    assert len(mounts) == 1
    assert mounts[0]["uuid"] == SDC1_UUID


async def test_api_create_disk_mount_without_udisks2(
    api_client_with_prefix: tuple[TestClient, str],
    coresys: CoreSys,
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
):
    """Test creating a disk mount without UDisks2 is a clean 400, not a 500.

    `resolve_device` raises DBusNotConnectedError, which is a
    HostNotSupportedError rather than a DBusError — so without an explicit
    check it would escape as an unexpected server error.
    """
    api_client, prefix = api_client_with_prefix

    with patch.object(
        type(coresys.dbus.udisks2),
        "is_connected",
        new_callable=PropertyMock,
        return_value=False,
    ):
        resp = await api_client.post(
            f"{prefix}/mounts",
            json={
                "name": "media_test",
                "type": "disk",
                "usage": "media",
                "device": "/dev/sdc1",
            },
        )

    assert resp.status == 400
    result = await resp.json()
    assert result["result"] == "error"
    assert result["error_key"] == "mount_disks_not_supported_error"

    resp = await api_client.get(f"{prefix}/mounts")
    result = await resp.json()
    assert result["data"]["mounts"] == []


async def test_api_create_disk_mount_rejects_system_disk(
    api_client_with_prefix: tuple[TestClient, str],
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
):
    """Test a disk excluded from candidates cannot be mounted by naming it.

    The candidates list and the create path share one guard, so a device
    hidden from the list is refused rather than quietly accepted.
    """
    api_client, prefix = api_client_with_prefix
    udisks2_manager_service: UDisks2ManagerService = all_dbus_services[
        "udisks2_manager"
    ]
    udisks2_manager_service.resolved_devices = [
        "/org/freedesktop/UDisks2/block_devices/sda1"
    ]

    resp = await api_client.post(
        f"{prefix}/mounts",
        json={
            "name": "media_test",
            "type": "disk",
            "usage": "media",
            "device": "/dev/sda1",
        },
    )

    assert resp.status == 400
    result = await resp.json()
    assert result["result"] == "error"
    assert result["error_key"] == "mount_device_protected_error"

    resp = await api_client.get(f"{prefix}/mounts")
    result = await resp.json()
    assert result["data"]["mounts"] == []
