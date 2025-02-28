"""Tests for mount manager."""

import json
import os
from pathlib import Path
from unittest.util import unorderable_list_difference

from dbus_fast import DBusError, ErrorType, Variant
from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.coresys import CoreSys
from supervisor.dbus.const import UnitActiveState
from supervisor.exceptions import (
    MountActivationError,
    MountError,
    MountJobError,
    MountNotFound,
)
from supervisor.mounts.manager import MountManager
from supervisor.mounts.mount import Mount
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion

from tests.common import mock_dbus_services
from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.systemd import Systemd as SystemdService
from tests.dbus_service_mocks.systemd_unit import SystemdUnit as SystemdUnitService

ERROR_NO_UNIT = DBusError("org.freedesktop.systemd1.NoSuchUnit", "error")
BACKUP_TEST_DATA = {
    "name": "backup_test",
    "type": "cifs",
    "usage": "backup",
    "server": "backup.local",
    "share": "backups",
}
MEDIA_TEST_DATA = {
    "name": "media_test",
    "type": "nfs",
    "usage": "media",
    "server": "media.local",
    "path": "/media",
}
SHARE_TEST_DATA = {
    "name": "share_test",
    "type": "nfs",
    "usage": "share",
    "server": "share.local",
    "path": "/share",
}


@pytest.fixture(name="mount")
async def fixture_mount(
    coresys: CoreSys, tmp_supervisor_data, path_extern, mount_propagation, mock_is_mount
) -> Mount:
    """Add an initial mount and load mounts."""
    mount = Mount.from_dict(coresys, MEDIA_TEST_DATA)
    coresys.mounts._mounts = {"media_test": mount}  # pylint: disable=protected-access
    await coresys.mounts.load()
    yield mount


async def test_load(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
):
    """Test mount manager loading."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.StartTransientUnit.calls.clear()

    backup_test = Mount.from_dict(coresys, BACKUP_TEST_DATA)
    media_test = Mount.from_dict(coresys, MEDIA_TEST_DATA)
    # pylint: disable=protected-access
    coresys.mounts._mounts = {
        "backup_test": backup_test,
        "media_test": media_test,
    }
    # pylint: enable=protected-access
    assert coresys.mounts.backup_mounts == [backup_test]
    assert coresys.mounts.media_mounts == [media_test]

    assert backup_test.state is None
    assert media_test.state is None
    assert not backup_test.local_where.exists()
    assert not media_test.local_where.exists()
    assert not any(coresys.config.path_media.iterdir())

    systemd_service.response_get_unit = {
        "mnt-data-supervisor-mounts-backup_test.mount": [
            ERROR_NO_UNIT,
            "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        ],
        "mnt-data-supervisor-mounts-media_test.mount": [
            ERROR_NO_UNIT,
            "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        ],
        "mnt-data-supervisor-media-media_test.mount": [
            ERROR_NO_UNIT,
            "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        ],
    }
    await coresys.mounts.load()

    assert backup_test.state == UnitActiveState.ACTIVE
    assert media_test.state == UnitActiveState.ACTIVE
    assert backup_test.local_where.is_dir()
    assert media_test.local_where.is_dir()
    assert (coresys.config.path_media / "media_test").is_dir()

    assert unorderable_list_difference(
        systemd_service.StartTransientUnit.calls,
        [
            (
                "mnt-data-supervisor-mounts-backup_test.mount",
                "fail",
                [
                    ["Options", Variant("s", "noserverino,guest")],
                    ["Type", Variant("s", "cifs")],
                    ["Description", Variant("s", "Supervisor cifs mount: backup_test")],
                    ["What", Variant("s", "//backup.local/backups")],
                ],
                [],
            ),
            (
                "mnt-data-supervisor-mounts-media_test.mount",
                "fail",
                [
                    ["Options", Variant("s", "soft,timeo=200")],
                    ["Type", Variant("s", "nfs")],
                    ["Description", Variant("s", "Supervisor nfs mount: media_test")],
                    ["What", Variant("s", "media.local:/media")],
                ],
                [],
            ),
            (
                "mnt-data-supervisor-media-media_test.mount",
                "fail",
                [
                    ["Options", Variant("s", "bind")],
                    [
                        "Description",
                        Variant("s", "Supervisor bind mount: bind_media_test"),
                    ],
                    ["What", Variant("s", "/mnt/data/supervisor/mounts/media_test")],
                ],
                [],
            ),
        ],
    ) == ([], [])


async def test_load_share_mount(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
):
    """Test mount manager loading with share mount."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.StartTransientUnit.calls.clear()

    share_test = Mount.from_dict(coresys, SHARE_TEST_DATA)
    # pylint: disable=protected-access
    coresys.mounts._mounts = {
        "share_test": share_test,
    }
    # pylint: enable=protected-access
    assert coresys.mounts.share_mounts == [share_test]

    assert share_test.state is None
    assert not share_test.local_where.exists()
    assert not any(coresys.config.path_share.iterdir())

    systemd_service.response_get_unit = {
        "mnt-data-supervisor-mounts-share_test.mount": [
            ERROR_NO_UNIT,
            "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        ],
        "mnt-data-supervisor-share-share_test.mount": [
            ERROR_NO_UNIT,
            "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        ],
    }
    await coresys.mounts.load()

    assert share_test.state == UnitActiveState.ACTIVE
    assert share_test.local_where.is_dir()
    assert (coresys.config.path_share / "share_test").is_dir()

    assert systemd_service.StartTransientUnit.calls == [
        (
            "mnt-data-supervisor-mounts-share_test.mount",
            "fail",
            [
                ["Options", Variant("s", "soft,timeo=200")],
                ["Type", Variant("s", "nfs")],
                ["Description", Variant("s", "Supervisor nfs mount: share_test")],
                ["What", Variant("s", "share.local:/share")],
            ],
            [],
        ),
        (
            "mnt-data-supervisor-share-share_test.mount",
            "fail",
            [
                ["Options", Variant("s", "bind")],
                ["Description", Variant("s", "Supervisor bind mount: bind_share_test")],
                ["What", Variant("s", "/mnt/data/supervisor/mounts/share_test")],
            ],
            [],
        ),
    ]


async def test_mount_failed_during_load(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    dbus_session_bus: MessageBus,
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
):
    """Test mount failed during load."""
    await mock_dbus_services(
        {"systemd_unit": "/org/freedesktop/systemd1/unit/tmp_test"}, dbus_session_bus
    )
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_unit_service: SystemdUnitService = all_dbus_services["systemd_unit"]
    systemd_service.StartTransientUnit.calls.clear()

    backup_test = Mount.from_dict(coresys, BACKUP_TEST_DATA)
    media_test = Mount.from_dict(coresys, MEDIA_TEST_DATA)
    # pylint: disable=protected-access
    coresys.mounts._mounts = {
        "backup_test": backup_test,
        "media_test": media_test,
    }
    # pylint: enable=protected-access

    assert backup_test.state is None
    assert media_test.state is None
    assert not backup_test.local_where.exists()
    assert not media_test.local_where.exists()
    assert not any(coresys.config.path_emergency.iterdir())
    assert not any(coresys.config.path_media.iterdir())

    assert coresys.resolution.issues == []
    assert coresys.resolution.suggestions == []

    systemd_service.response_get_unit = {
        "mnt-data-supervisor-mounts-backup_test.mount": [
            ERROR_NO_UNIT,
            "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        ],
        "mnt-data-supervisor-mounts-media_test.mount": [
            ERROR_NO_UNIT,
            "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        ],
        "mnt-data-supervisor-media-media_test.mount": [
            ERROR_NO_UNIT,
            "/org/freedesktop/systemd1/unit/tmp_test",
        ],
    }
    systemd_unit_service.active_state = "failed"
    await coresys.mounts.load()

    assert backup_test.state == UnitActiveState.FAILED
    assert media_test.state == UnitActiveState.FAILED
    assert backup_test.local_where.is_dir()
    assert media_test.local_where.is_dir()
    assert (coresys.config.path_media / "media_test").is_dir()
    emergency_dir = coresys.config.path_emergency / "media_test"
    assert emergency_dir.is_dir()
    assert os.access(emergency_dir, os.R_OK)
    assert not os.access(emergency_dir, os.W_OK)

    assert (
        Issue(IssueType.MOUNT_FAILED, ContextType.MOUNT, reference="backup_test")
        in coresys.resolution.issues
    )
    assert (
        Suggestion(
            SuggestionType.EXECUTE_RELOAD, ContextType.MOUNT, reference="backup_test"
        )
        in coresys.resolution.suggestions
    )
    assert (
        Suggestion(
            SuggestionType.EXECUTE_REMOVE, ContextType.MOUNT, reference="backup_test"
        )
        in coresys.resolution.suggestions
    )
    assert (
        Issue(IssueType.MOUNT_FAILED, ContextType.MOUNT, reference="media_test")
        in coresys.resolution.issues
    )
    assert (
        Suggestion(
            SuggestionType.EXECUTE_RELOAD, ContextType.MOUNT, reference="media_test"
        )
        in coresys.resolution.suggestions
    )
    assert (
        Suggestion(
            SuggestionType.EXECUTE_REMOVE, ContextType.MOUNT, reference="media_test"
        )
        in coresys.resolution.suggestions
    )

    assert len(systemd_service.StartTransientUnit.calls) == 3
    assert systemd_service.StartTransientUnit.calls[2] == (
        "mnt-data-supervisor-media-media_test.mount",
        "fail",
        [
            ["Options", Variant("s", "ro,bind")],
            [
                "Description",
                Variant("s", "Supervisor bind mount: emergency_media_test"),
            ],
            ["What", Variant("s", "/mnt/data/supervisor/emergency/media_test")],
        ],
        [],
    )


async def test_create_mount(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    mock_is_mount,
):
    """Test creating a mount."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.StartTransientUnit.calls.clear()

    await coresys.mounts.load()

    mount = Mount.from_dict(coresys, MEDIA_TEST_DATA)

    assert mount.state is None
    assert mount not in coresys.mounts
    assert "media_test" not in coresys.mounts
    assert not mount.local_where.exists()
    assert not any(coresys.config.path_media.iterdir())

    # Create the mount
    systemd_service.response_get_unit = [
        ERROR_NO_UNIT,
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        ERROR_NO_UNIT,
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
    ]
    await coresys.mounts.create_mount(mount)

    assert mount.state == UnitActiveState.ACTIVE
    assert mount in coresys.mounts
    assert "media_test" in coresys.mounts
    assert mount.local_where.exists()
    assert (coresys.config.path_media / "media_test").exists()

    assert [call[0] for call in systemd_service.StartTransientUnit.calls] == [
        "mnt-data-supervisor-mounts-media_test.mount",
        "mnt-data-supervisor-media-media_test.mount",
    ]


async def test_update_mount(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    mount: Mount,
):
    """Test updating a mount."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_unit_service: SystemdUnitService = all_dbus_services["systemd_unit"]
    systemd_service.mock_systemd_unit = systemd_unit_service
    systemd_service.StartTransientUnit.calls.clear()
    systemd_service.StopUnit.calls.clear()

    # Update the mount. Should be unmounted then remounted
    mount_new = Mount.from_dict(coresys, MEDIA_TEST_DATA)
    assert mount.state == UnitActiveState.ACTIVE
    assert mount_new.state is None

    systemd_service.response_get_unit = [
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        ERROR_NO_UNIT,
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        ERROR_NO_UNIT,
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
    ]
    await coresys.mounts.create_mount(mount_new)

    assert mount.state is None
    assert mount_new.state == UnitActiveState.ACTIVE

    assert [call[0] for call in systemd_service.StartTransientUnit.calls] == [
        "mnt-data-supervisor-mounts-media_test.mount",
        "mnt-data-supervisor-media-media_test.mount",
    ]
    assert [call[0] for call in systemd_service.StopUnit.calls] == [
        "mnt-data-supervisor-media-media_test.mount",
        "mnt-data-supervisor-mounts-media_test.mount",
    ]


async def test_reload_mount(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    mount: Mount,
):
    """Test reloading a mount."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.ReloadOrRestartUnit.calls.clear()

    # Reload the mount
    systemd_service.response_get_unit = [
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount"
    ]
    await coresys.mounts.reload_mount(mount.name)

    assert len(systemd_service.ReloadOrRestartUnit.calls) == 1
    assert (
        systemd_service.ReloadOrRestartUnit.calls[0][0]
        == "mnt-data-supervisor-mounts-media_test.mount"
    )


async def test_remove_mount(
    coresys: CoreSys, all_dbus_services: dict[str, DBusServiceMock], mount: Mount
):
    """Test removing a mount."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_unit_service: SystemdUnitService = all_dbus_services["systemd_unit"]
    systemd_unit_service.active_state = ["active", "inactive", "active", "inactive"]
    systemd_service.StopUnit.calls.clear()

    # Remove the mount
    assert mount == await coresys.mounts.remove_mount(mount.name)

    assert mount.state is None
    assert mount not in coresys.mounts

    assert [call[0] for call in systemd_service.StopUnit.calls] == [
        "mnt-data-supervisor-media-media_test.mount",
        "mnt-data-supervisor-mounts-media_test.mount",
    ]


async def test_remove_reload_mount_missing(coresys: CoreSys, mount_propagation):
    """Test removing or reloading a non existent mount errors."""
    await coresys.mounts.load()

    with pytest.raises(MountNotFound):
        await coresys.mounts.remove_mount("does_not_exist")

    with pytest.raises(MountNotFound):
        await coresys.mounts.reload_mount("does_not_exist")


async def test_save_data(
    coresys: CoreSys,
    tmp_supervisor_data: Path,
    path_extern,
    mount_propagation,
    mock_is_mount,
):
    """Test saving mount config data."""
    # Replace mount manager with one that doesn't have save_data mocked
    coresys._mounts = await MountManager(coresys).load_config()  # pylint: disable=protected-access

    path = tmp_supervisor_data / "mounts.json"
    assert not path.exists()

    await coresys.mounts.load()
    await coresys.mounts.create_mount(
        Mount.from_dict(
            coresys,
            {
                "name": "auth_test",
                "type": "cifs",
                "usage": "backup",
                "server": "backup.local",
                "share": "backups",
                "username": "admin",
                "password": "password",
            },
        )
    )
    await coresys.mounts.save_data()

    assert path.exists()
    with path.open() as file:
        config = json.load(file)
        assert config["mounts"] == [
            {
                "version": None,
                "name": "auth_test",
                "type": "cifs",
                "usage": "backup",
                "server": "backup.local",
                "share": "backups",
                "username": "admin",
                "password": "password",
                "read_only": False,
            }
        ]


async def test_create_mount_start_unit_failure(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
):
    """Test failure to start mount unit does not add mount to the list."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.StartTransientUnit.calls.clear()
    systemd_service.ResetFailedUnit.calls.clear()
    systemd_service.StopUnit.calls.clear()

    systemd_service.response_get_unit = ERROR_NO_UNIT
    systemd_service.response_start_transient_unit = DBusError(ErrorType.FAILED, "fail")

    await coresys.mounts.load()

    mount = Mount.from_dict(coresys, BACKUP_TEST_DATA)

    with pytest.raises(MountError):
        await coresys.mounts.create_mount(mount)

    assert mount.state is None
    assert mount not in coresys.mounts

    assert len(systemd_service.StartTransientUnit.calls) == 1
    assert not systemd_service.ResetFailedUnit.calls
    assert not systemd_service.StopUnit.calls


async def test_create_mount_activation_failure(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
):
    """Test activation failure during create mount does not add mount to the list and unmounts new mount."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_unit_service: SystemdUnitService = all_dbus_services["systemd_unit"]

    systemd_service.StartTransientUnit.calls.clear()
    systemd_service.ResetFailedUnit.calls.clear()
    systemd_service.StopUnit.calls.clear()

    systemd_service.response_get_unit = [
        ERROR_NO_UNIT,
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
    ]
    systemd_unit_service.active_state = ["failed", "failed", "failed"]

    await coresys.mounts.load()

    mount = Mount.from_dict(coresys, BACKUP_TEST_DATA)

    with pytest.raises(MountActivationError):
        await coresys.mounts.create_mount(mount)

    assert mount.state is None
    assert mount not in coresys.mounts

    assert len(systemd_service.StartTransientUnit.calls) == 1
    assert len(systemd_service.ResetFailedUnit.calls) == 1
    assert not systemd_service.StopUnit.calls


async def test_reload_mounts(
    coresys: CoreSys, all_dbus_services: dict[str, DBusServiceMock], mount: Mount
):
    """Test reloading mounts."""
    systemd_unit_service: SystemdUnitService = all_dbus_services["systemd_unit"]
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.ReloadOrRestartUnit.calls.clear()

    assert mount.state == UnitActiveState.ACTIVE
    assert mount.failed_issue not in coresys.resolution.issues

    systemd_unit_service.active_state = "failed"
    await coresys.mounts.reload()

    assert mount.state == UnitActiveState.FAILED
    assert mount.failed_issue in coresys.resolution.issues
    assert len(coresys.resolution.suggestions_for_issue(mount.failed_issue)) == 2
    assert len(systemd_service.ReloadOrRestartUnit.calls) == 1

    # This should now remove the issue from the list
    systemd_unit_service.active_state = "active"
    await coresys.mounts.reload()

    assert mount.state == UnitActiveState.ACTIVE
    assert mount.failed_issue not in coresys.resolution.issues
    assert not coresys.resolution.suggestions_for_issue(mount.failed_issue)


async def test_reload_mounts_attempts_initial_mount(
    coresys: CoreSys, all_dbus_services: dict[str, DBusServiceMock], mount: Mount
):
    """Test reloading mounts attempts initial mount."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.StartTransientUnit.calls.clear()
    systemd_service.response_get_unit = [
        ERROR_NO_UNIT,
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        ERROR_NO_UNIT,
        ERROR_NO_UNIT,
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
    ]
    systemd_service.response_reload_or_restart_unit = ERROR_NO_UNIT
    coresys.mounts.bound_mounts[0].emergency = True

    await coresys.mounts.reload()

    assert systemd_service.StartTransientUnit.calls == [
        (
            "mnt-data-supervisor-mounts-media_test.mount",
            "fail",
            [
                ["Options", Variant("s", "soft,timeo=200")],
                ["Type", Variant("s", "nfs")],
                ["Description", Variant("s", "Supervisor nfs mount: media_test")],
                ["What", Variant("s", "media.local:/media")],
            ],
            [],
        ),
        (
            "mnt-data-supervisor-media-media_test.mount",
            "fail",
            [
                ["Options", Variant("s", "bind")],
                ["Description", Variant("s", "Supervisor bind mount: bind_media_test")],
                ["What", Variant("s", "/mnt/data/supervisor/mounts/media_test")],
            ],
            [],
        ),
    ]


@pytest.mark.parametrize("os_available", ["9.5"], indirect=True)
async def test_mounting_not_supported(
    coresys: CoreSys,
    caplog: pytest.LogCaptureFixture,
    os_available,
):
    """Test mounting not supported on system."""
    caplog.clear()

    await coresys.mounts.load()
    assert not caplog.text

    mount = Mount.from_dict(coresys, MEDIA_TEST_DATA)
    coresys.mounts._mounts = {"media_test": mount}  # pylint: disable=protected-access

    # Only tell the user about an issue here if they actually have mounts we couldn't load
    # This is an edge case but users can downgrade OS so its possible
    await coresys.mounts.load()
    assert "Cannot load configured mounts" in caplog.text

    with pytest.raises(MountJobError):
        await coresys.mounts.create_mount(mount)

    with pytest.raises(MountJobError):
        await coresys.mounts.reload_mount("media_test")

    with pytest.raises(MountJobError):
        await coresys.mounts.remove_mount("media_test")


async def test_create_share_mount(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    mock_is_mount,
):
    """Test creating a share mount."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.StartTransientUnit.calls.clear()

    await coresys.mounts.load()

    mount = Mount.from_dict(coresys, SHARE_TEST_DATA)

    assert mount.state is None
    assert mount not in coresys.mounts
    assert "share_test" not in coresys.mounts
    assert not mount.local_where.exists()
    assert not any(coresys.config.path_share.iterdir())

    # Create the mount
    systemd_service.response_get_unit = [
        ERROR_NO_UNIT,
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        ERROR_NO_UNIT,
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
    ]
    await coresys.mounts.create_mount(mount)

    assert mount.state == UnitActiveState.ACTIVE
    assert mount in coresys.mounts
    assert "share_test" in coresys.mounts
    assert mount.local_where.exists()
    assert (coresys.config.path_share / "share_test").exists()

    assert [call[0] for call in systemd_service.StartTransientUnit.calls] == [
        "mnt-data-supervisor-mounts-share_test.mount",
        "mnt-data-supervisor-share-share_test.mount",
    ]
