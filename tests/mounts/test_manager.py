"""Tests for mount manager."""

import errno
import json
from pathlib import Path
from unittest.mock import patch
from unittest.util import unorderable_list_difference

from dbus_fast import DBusError, ErrorType
from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.coresys import CoreSys
from supervisor.dbus.const import UnitActiveState
from supervisor.exceptions import (
    MountActivationError,
    MountError,
    MountJobError,
    MountNotFound,
    MountTargetNotDirectoryError,
    MountTargetNotEmptyError,
)
from supervisor.mounts.manager import MountManager
from supervisor.mounts.mount import Mount
from supervisor.resolution.const import ContextType, IssueType, SuggestionType
from supervisor.resolution.data import Issue, Suggestion

from tests.common import mock_dbus_services, mount_start_transient_unit_call
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
    return mount


async def test_load(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    mock_is_mount,
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
            ERROR_NO_UNIT,
            "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        ],
        "mnt-data-supervisor-mounts-backup_test.automount": [ERROR_NO_UNIT],
        "mnt-data-supervisor-media-media_test.mount": [
            ERROR_NO_UNIT,
            ERROR_NO_UNIT,
            "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        ],
        "mnt-data-supervisor-media-media_test.automount": [ERROR_NO_UNIT],
        "mnt-data-supervisor-mounts-media_test.mount": [ERROR_NO_UNIT],
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
            mount_start_transient_unit_call(
                automount_unit="mnt-data-supervisor-mounts-backup_test.automount",
                mount_unit="mnt-data-supervisor-mounts-backup_test.mount",
                where="/mnt/data/supervisor/mounts/backup_test",
                description="Supervisor cifs mount: backup_test",
                what="//backup.local/backups",
                fstype="cifs",
                options="noserverino,soft,echo_interval=10,retrans=0,guest",
            ),
            mount_start_transient_unit_call(
                automount_unit="mnt-data-supervisor-media-media_test.automount",
                mount_unit="mnt-data-supervisor-media-media_test.mount",
                where="/mnt/data/supervisor/media/media_test",
                description="Supervisor nfs mount: media_test",
                what="media.local:/media",
                fstype="nfs",
                options="softerr,timeo=100,retrans=2",
            ),
        ],
    ) == ([], [])


async def test_load_share_mount(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    mock_is_mount,
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
        "mnt-data-supervisor-share-share_test.mount": [
            ERROR_NO_UNIT,
            ERROR_NO_UNIT,
            "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        ],
        "mnt-data-supervisor-share-share_test.automount": [ERROR_NO_UNIT],
        "mnt-data-supervisor-mounts-share_test.mount": [ERROR_NO_UNIT],
    }
    await coresys.mounts.load()

    assert share_test.state == UnitActiveState.ACTIVE
    assert share_test.local_where.is_dir()
    assert (coresys.config.path_share / "share_test").is_dir()

    assert systemd_service.StartTransientUnit.calls == [
        mount_start_transient_unit_call(
            automount_unit="mnt-data-supervisor-share-share_test.automount",
            mount_unit="mnt-data-supervisor-share-share_test.mount",
            where="/mnt/data/supervisor/share/share_test",
            description="Supervisor nfs mount: share_test",
            what="share.local:/share",
            fstype="nfs",
            options="softerr,timeo=100,retrans=2",
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
    assert not any(coresys.config.path_media.iterdir())

    assert coresys.resolution.issues == []
    assert coresys.resolution.suggestions == []

    systemd_service.response_get_unit = {
        "mnt-data-supervisor-mounts-backup_test.mount": [
            ERROR_NO_UNIT,
            ERROR_NO_UNIT,
            "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        ],
        "mnt-data-supervisor-mounts-backup_test.automount": [ERROR_NO_UNIT],
        "mnt-data-supervisor-media-media_test.mount": [
            ERROR_NO_UNIT,
            ERROR_NO_UNIT,
            "/org/freedesktop/systemd1/unit/tmp_test",
        ],
        "mnt-data-supervisor-media-media_test.automount": [ERROR_NO_UNIT],
        "mnt-data-supervisor-mounts-media_test.mount": [ERROR_NO_UNIT],
    }
    systemd_unit_service.active_state = "failed"
    await coresys.mounts.load()

    # Both mounts failed activation. Resolution issues are surfaced and
    # suggest reload/remove. The dropped "emergency fallback" of the
    # old bind layer no longer applies — containers will see ETIMEDOUT
    # on access until the user fixes or removes the mount.
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
    assert len(systemd_service.StartTransientUnit.calls) == 2


async def test_load_adopted_mount_probe_failure_creates_issue(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
):
    """Test adopting an active pair whose probe fails surfaces an issue."""
    media_test = Mount.from_dict(coresys, MEDIA_TEST_DATA)
    # pylint: disable-next=protected-access
    coresys.mounts._mounts = {"media_test": media_test}

    assert coresys.resolution.issues == []

    # Both units exist and the .automount is active (mock defaults), but
    # the server does not answer the probe.
    with patch(
        "supervisor.mounts.mount._probe_network_mount",
        side_effect=OSError(errno.EHOSTDOWN, "Host is down"),
    ):
        await coresys.mounts.load()

    assert media_test.failed_issue in coresys.resolution.issues
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

    # Create the mount. GetUnit sequence: .mount, .automount, both legacy
    # unit checks, then the post-mount refresh.
    systemd_service.response_get_unit = [
        ERROR_NO_UNIT,
        ERROR_NO_UNIT,
        ERROR_NO_UNIT,
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
        "mnt-data-supervisor-media-media_test.automount",
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

    # remove_mount finds the existing unit, unmount() runs, then
    # mount_new.load() finds neither unit nor automount nor legacy
    # leftovers and creates a fresh transient .automount + .mount pair.
    # The legacy data unit check runs after the post-mount refresh.
    systemd_service.response_get_unit = [
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        ERROR_NO_UNIT,
        ERROR_NO_UNIT,
        ERROR_NO_UNIT,
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        ERROR_NO_UNIT,
    ]
    await coresys.mounts.create_mount(mount_new)

    assert mount.state is None
    assert mount_new.state == UnitActiveState.ACTIVE

    assert [call[0] for call in systemd_service.StartTransientUnit.calls] == [
        "mnt-data-supervisor-media-media_test.automount",
    ]
    # Network mount unmount stops the .automount companion first, then
    # the .mount itself.
    assert [call[0] for call in systemd_service.StopUnit.calls] == [
        "mnt-data-supervisor-media-media_test.automount",
        "mnt-data-supervisor-media-media_test.mount",
    ]


async def test_load_migrates_legacy_layout(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    mock_is_mount,
):
    """Test load tears down eager-mount era units before arming the automount.

    On a warm upgrade the old design's bind unit occupies the exact unit
    name the network .mount uses now, and the old data mount lives on at
    the legacy location. Both must be stopped before the trigger can be
    armed at the path.
    """
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.StartTransientUnit.calls.clear()
    systemd_service.StopUnit.calls.clear()

    mount = Mount.from_dict(coresys, MEDIA_TEST_DATA)
    coresys.mounts._mounts = {"media_test": mount}  # pylint: disable=protected-access

    systemd_service.response_get_unit = {
        "mnt-data-supervisor-media-media_test.mount": [
            "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
            "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
            "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        ],
        "mnt-data-supervisor-media-media_test.automount": [ERROR_NO_UNIT],
        "mnt-data-supervisor-mounts-media_test.mount": [
            "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount"
        ],
    }
    await coresys.mounts.load()

    assert mount.state == UnitActiveState.ACTIVE
    assert [call[0] for call in systemd_service.StopUnit.calls] == [
        "mnt-data-supervisor-media-media_test.mount",
        "mnt-data-supervisor-mounts-media_test.mount",
    ]
    assert [call[0] for call in systemd_service.StartTransientUnit.calls] == [
        "mnt-data-supervisor-media-media_test.automount",
    ]


async def test_load_migrates_legacy_layout_dead_data_mount(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    mock_is_mount,
    caplog: pytest.LogCaptureFixture,
):
    """Test warm upgrade succeeds when the legacy data mount cannot stop.

    The eager-mount-era data mount conflicts with nothing; a failed stop
    (e.g. unmount timing out against an unreachable server) must not fail
    the automount setup — the path would otherwise be left a plain
    writable directory without an armed trigger.
    """
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_unit_service: SystemdUnitService = all_dbus_services["systemd_unit"]
    systemd_service.mock_systemd_unit = systemd_unit_service
    systemd_unit_service.active_state = "active"
    systemd_service.StopUnit.calls.clear()
    systemd_service.StartTransientUnit.calls.clear()

    mount = Mount.from_dict(coresys, MEDIA_TEST_DATA)
    coresys.mounts._mounts = {"media_test": mount}  # pylint: disable=protected-access

    systemd_service.response_get_unit = {
        "mnt-data-supervisor-media-media_test.mount": [
            "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
            "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
            "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        ],
        "mnt-data-supervisor-media-media_test.automount": [ERROR_NO_UNIT],
        "mnt-data-supervisor-mounts-media_test.mount": [
            "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount"
        ],
    }
    # Legacy bind stop succeeds, legacy data mount stop fails
    systemd_service.response_stop_unit = [
        "/org/freedesktop/systemd1/job/7623",
        DBusError(ErrorType.FAILED, "Job timed out"),
    ]
    await coresys.mounts.load()

    assert mount.state == UnitActiveState.ACTIVE
    assert mount.failed_issue not in coresys.resolution.issues
    # The automount was armed before the legacy data mount stop was tried
    assert [call[0] for call in systemd_service.StartTransientUnit.calls] == [
        "mnt-data-supervisor-media-media_test.automount",
    ]
    assert (
        "Could not stop legacy unit mnt-data-supervisor-mounts-media_test.mount"
        in caplog.text
    )


async def test_reload_mount_rearms_missing_trigger(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    mount: Mount,
):
    """Test reload re-creates the unit pair when the automount trigger is gone."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.StartTransientUnit.calls.clear()
    systemd_service.StopUnit.calls.clear()
    systemd_service.ResetFailedUnit.calls.clear()

    # .mount lookups: once by the full unmount (the .mount may still be
    # attached and must be stopped), once by the post-mount refresh.
    systemd_service.response_get_unit = {
        "mnt-data-supervisor-media-media_test.automount": [ERROR_NO_UNIT],
        "mnt-data-supervisor-media-media_test.mount": [
            "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
            "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        ],
    }
    await coresys.mounts.reload_mount(mount.name)

    assert systemd_service.StopUnit.calls == [
        ("mnt-data-supervisor-media-media_test.automount", "fail"),
        ("mnt-data-supervisor-media-media_test.mount", "fail"),
    ]
    assert [call[0] for call in systemd_service.ResetFailedUnit.calls] == [
        "mnt-data-supervisor-media-media_test.automount",
        "mnt-data-supervisor-media-media_test.mount",
    ]
    assert [call[0] for call in systemd_service.StartTransientUnit.calls] == [
        "mnt-data-supervisor-media-media_test.automount",
    ]


async def test_reload_mount_healthy_skips_systemd(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    mount: Mount,
):
    """A healthy mount (probe passes) triggers no systemd operations at all."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.ReloadOrRestartUnit.calls.clear()
    systemd_service.StartTransientUnit.calls.clear()
    systemd_service.StopUnit.calls.clear()

    await coresys.mounts.reload_mount(mount.name)

    assert systemd_service.ReloadOrRestartUnit.calls == []
    assert systemd_service.StopUnit.calls == []
    assert systemd_service.StartTransientUnit.calls == []


async def test_reload_mount_probe_failure_surfaces_resolution_issue(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    mount: Mount,
):
    """A failed probe surfaces a resolution issue and raises.

    The supervisor no longer issues a systemd reload here — autofs
    will re-trigger the underlying `.mount` when something next
    accesses the path. The API caller gets the error so it can
    surface the failure to the user.
    """
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.ReloadOrRestartUnit.calls.clear()

    with (
        patch(
            "supervisor.mounts.mount._probe_network_mount",
            side_effect=OSError(errno.EHOSTDOWN, "Host is down"),
        ),
        pytest.raises(MountActivationError),
    ):
        await coresys.mounts.reload_mount(mount.name)

    assert systemd_service.ReloadOrRestartUnit.calls == []
    assert mount.failed_issue in coresys.resolution.issues


async def test_reload_mount_escalates_to_unit_recreation(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    mount: Mount,
):
    """Test reload re-creates the unit pair when the probe keeps failing.

    An established mount whose session is permanently dead never
    re-triggers on its own — reload escalates once to a full unmount +
    mount. If the share is still unreachable through the fresh pair the
    error and issue surface to the caller.
    """
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.StartTransientUnit.calls.clear()
    systemd_service.StopUnit.calls.clear()

    with (
        patch(
            "supervisor.mounts.mount._probe_network_mount",
            side_effect=OSError(errno.EHOSTDOWN, "Host is down"),
        ),
        pytest.raises(MountActivationError),
    ):
        await coresys.mounts.reload_mount(mount.name)

    assert systemd_service.StopUnit.calls == [
        ("mnt-data-supervisor-media-media_test.automount", "fail"),
        ("mnt-data-supervisor-media-media_test.mount", "fail"),
    ]
    assert [call[0] for call in systemd_service.StartTransientUnit.calls] == [
        "mnt-data-supervisor-media-media_test.automount",
    ]
    assert mount.failed_issue in coresys.resolution.issues

    # Once the share answers again (probe passes via mock_is_mount from
    # the mount fixture), reload does not escalate: no systemd operations
    # and the issue is dismissed.
    systemd_service.StartTransientUnit.calls.clear()
    systemd_service.StopUnit.calls.clear()

    await coresys.mounts.reload_mount(mount.name)

    assert systemd_service.StopUnit.calls == []
    assert systemd_service.StartTransientUnit.calls == []
    assert mount.failed_issue not in coresys.resolution.issues


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
        "mnt-data-supervisor-media-media_test.automount",
        "mnt-data-supervisor-media-media_test.mount",
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


async def test_load_local_data_creates_issue(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    mock_is_mount,
):
    """Test local data blocking the mount target at load creates a repair issue."""
    systemd_service: SystemdService = all_dbus_services["systemd"]

    mount = Mount.from_dict(coresys, MEDIA_TEST_DATA)
    coresys.mounts._mounts = {"media_test": mount}  # pylint: disable=protected-access

    media_dir = coresys.config.path_media / "media_test"
    media_dir.mkdir()
    (media_dir / "recording.mp4").touch()

    systemd_service.response_get_unit = ERROR_NO_UNIT
    await coresys.mounts.load()

    issue = Issue(IssueType.MOUNT_FAILED, ContextType.MOUNT, reference="media_test")
    assert issue in coresys.resolution.issues
    assert coresys.resolution.suggestions_for_issue(issue) == {
        Suggestion(
            SuggestionType.MOVE_LOCAL_DATA, ContextType.MOUNT, reference="media_test"
        ),
        Suggestion(
            SuggestionType.EXECUTE_RELOAD, ContextType.MOUNT, reference="media_test"
        ),
        Suggestion(
            SuggestionType.EXECUTE_REMOVE, ContextType.MOUNT, reference="media_test"
        ),
    }


async def test_reload_mount_dismisses_local_data_issue(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    mount: Mount,
):
    """Test a successful reload dismisses a stale local data issue."""
    systemd_service: SystemdService = all_dbus_services["systemd"]

    coresys.resolution.create_issue(
        IssueType.MOUNT_FAILED,
        ContextType.MOUNT,
        reference="media_test",
        suggestions=[
            SuggestionType.MOVE_LOCAL_DATA,
            SuggestionType.EXECUTE_RELOAD,
            SuggestionType.EXECUTE_REMOVE,
        ],
    )

    systemd_service.response_get_unit = [
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        ERROR_NO_UNIT,
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
    ]
    await coresys.mounts.reload_mount(mount.name)

    assert coresys.resolution.issues == []
    assert coresys.resolution.suggestions == []


async def test_relocate_local_data_recovery_name_collision(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    mount: Mount,
):
    """Test relocating local data picks a free recovery folder name."""
    media_dir = coresys.config.path_media / "media_test"
    media_dir.mkdir(exist_ok=True)
    (media_dir / "recording.mp4").touch()
    (coresys.config.path_media / "media_test_local_recovery").mkdir()

    await coresys.mounts.relocate_local_data(mount.name)

    recovery_dir = coresys.config.path_media / "media_test_local_recovery_2"
    assert (recovery_dir / "recording.mp4").exists()
    assert media_dir.is_dir()
    assert not any(media_dir.iterdir())


async def test_create_mount_blocked_by_existing_local_data(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    mock_is_mount,
):
    """Test creating a media mount fails fast if the media directory has local data."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.StartTransientUnit.calls.clear()

    await coresys.mounts.load()

    media_dir = coresys.config.path_media / "media_test"
    media_dir.mkdir()
    (media_dir / "recording.mp4").touch()

    with pytest.raises(MountTargetNotEmptyError):
        await coresys.mounts.create_mount(Mount.from_dict(coresys, MEDIA_TEST_DATA))

    assert "media_test" not in coresys.mounts
    assert systemd_service.StartTransientUnit.calls == []


async def test_create_mount_blocked_by_non_directory_target(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    mount_propagation,
    mock_is_mount,
):
    """Test creating a media mount fails fast if the media target is not a directory."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.StartTransientUnit.calls.clear()

    await coresys.mounts.load()

    (coresys.config.path_media / "media_test").touch()

    with pytest.raises(MountTargetNotDirectoryError):
        await coresys.mounts.create_mount(Mount.from_dict(coresys, MEDIA_TEST_DATA))

    assert "media_test" not in coresys.mounts
    assert systemd_service.StartTransientUnit.calls == []


async def test_update_mount_blocked_by_existing_local_data(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    mount: Mount,
):
    """Test updating a mount fails fast on local data without touching the mount.

    Simulates the state after systemd tore down the bind mount and an add-on
    wrote into the bare media directory: the update must not unmount the data
    mount just to fail on the non-empty bind target afterwards.
    """
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.StopUnit.calls.clear()

    media_dir = coresys.config.path_media / "media_test"
    media_dir.mkdir(exist_ok=True)
    (media_dir / "recording.mp4").touch()

    with pytest.raises(MountTargetNotEmptyError):
        await coresys.mounts.create_mount(Mount.from_dict(coresys, MEDIA_TEST_DATA))

    assert mount == coresys.mounts.get("media_test")
    assert mount.state == UnitActiveState.ACTIVE
    assert systemd_service.StopUnit.calls == []


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
    # Rollback runs a best-effort cleanup for units that were never
    # created: a stop of the .automount and failure-state resets.
    assert [call[0] for call in systemd_service.StopUnit.calls] == [
        "mnt-data-supervisor-mounts-backup_test.automount"
    ]
    assert [call[0] for call in systemd_service.ResetFailedUnit.calls] == [
        "mnt-data-supervisor-mounts-backup_test.automount",
        "mnt-data-supervisor-mounts-backup_test.mount",
    ]


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
        ERROR_NO_UNIT,
        ERROR_NO_UNIT,
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
    ]
    systemd_unit_service.active_state = ["failed", "failed"]

    await coresys.mounts.load()

    mount = Mount.from_dict(coresys, BACKUP_TEST_DATA)

    with pytest.raises(MountActivationError):
        await coresys.mounts.create_mount(mount)

    assert mount.state is None
    assert mount not in coresys.mounts

    assert len(systemd_service.StartTransientUnit.calls) == 1
    # Cleanup unmount stops the .automount (best-effort); the failed
    # .mount is left to the failure-state resets, which cover both units.
    assert [call[0] for call in systemd_service.StopUnit.calls] == [
        "mnt-data-supervisor-mounts-backup_test.automount",
    ]
    assert [call[0] for call in systemd_service.ResetFailedUnit.calls] == [
        "mnt-data-supervisor-mounts-backup_test.automount",
        "mnt-data-supervisor-mounts-backup_test.mount",
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

    # Create the mount. GetUnit sequence: .mount, .automount, both legacy
    # unit checks, then the post-mount refresh.
    systemd_service.response_get_unit = [
        ERROR_NO_UNIT,
        ERROR_NO_UNIT,
        ERROR_NO_UNIT,
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
        "mnt-data-supervisor-share-share_test.automount",
    ]


async def test_reload_reconciles_issue_dismissal(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    mount: Mount,
):
    """Test the periodic reconcile dismisses the issue once the mount is healthy."""
    coresys.resolution.create_issue(
        IssueType.MOUNT_FAILED,
        ContextType.MOUNT,
        reference="media_test",
        suggestions=[SuggestionType.EXECUTE_RELOAD, SuggestionType.EXECUTE_REMOVE],
    )

    await coresys.mounts.reload()

    assert mount.failed_issue not in coresys.resolution.issues
    assert not coresys.resolution.suggestions_for_issue(mount.failed_issue)


async def test_reload_reconciles_issue_creation(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    mount: Mount,
):
    """Test the periodic reconcile surfaces an unreachable mount as issue."""
    assert mount.failed_issue not in coresys.resolution.issues

    with patch(
        "supervisor.mounts.mount._probe_network_mount",
        side_effect=OSError(errno.EHOSTDOWN, "Host is down"),
    ):
        await coresys.mounts.reload()

    assert mount.state == UnitActiveState.INACTIVE
    assert mount.failed_issue in coresys.resolution.issues
    assert len(coresys.resolution.suggestions_for_issue(mount.failed_issue)) == 2


@pytest.mark.parametrize(
    ("error", "expected_suggestions"),
    [
        (
            MountTargetNotEmptyError(name="media_test", path="/media/media_test"),
            {
                SuggestionType.MOVE_LOCAL_DATA,
                SuggestionType.EXECUTE_RELOAD,
                SuggestionType.EXECUTE_REMOVE,
            },
        ),
        (
            MountError("Test trigger repair failure"),
            {SuggestionType.EXECUTE_RELOAD, SuggestionType.EXECUTE_REMOVE},
        ),
    ],
)
async def test_reload_reconciles_trigger_repair_failure(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    mount: Mount,
    error: MountError,
    expected_suggestions: set[SuggestionType],
):
    """Test the reconcile surfaces a failed trigger repair as issue."""
    assert mount.failed_issue not in coresys.resolution.issues

    with patch.object(Mount, "repair_trigger", side_effect=error):
        await coresys.mounts.reload()

    assert mount.failed_issue in coresys.resolution.issues
    assert {
        suggestion.type
        for suggestion in coresys.resolution.suggestions_for_issue(mount.failed_issue)
    } == expected_suggestions
