"""Tests for mounts."""

from __future__ import annotations

import asyncio
from dataclasses import replace
import errno
from pathlib import Path, PurePath
import stat
from typing import Any
from unittest.mock import ANY, MagicMock, PropertyMock, patch

from dbus_fast import DBusError, ErrorType
import pytest

from supervisor.coresys import CoreSys
from supervisor.dbus.const import UnitActiveState
from supervisor.exceptions import (
    DBusError as SupervisorDBusError,
    MountActivationError,
    MountDeviceNotFoundError,
    MountDeviceReadOnlyError,
    MountDisksNotSupportedError,
    MountError,
    MountFilesystemNotSupportedError,
    MountInvalidError,
    MountSetupError,
    MountUnmountError,
)
from supervisor.mounts.const import MountCifsVersion, MountType, MountUsage
from supervisor.mounts.mount import CIFSMount, DiskMount, Mount, NFSMount

from tests.common import mount_start_transient_unit_call
from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.systemd import Systemd as SystemdService
from tests.dbus_service_mocks.systemd_unit import SystemdUnit as SystemdUnitService
from tests.dbus_service_mocks.udisks2_manager import (
    UDisks2Manager as UDisks2ManagerService,
)

ERROR_FAILURE = DBusError(ErrorType.FAILED, "error")
ERROR_NO_UNIT = DBusError("org.freedesktop.systemd1.NoSuchUnit", "error")

SDB1_OBJECT_PATH = "/org/freedesktop/UDisks2/block_devices/sdb1"
SDC1_OBJECT_PATH = "/org/freedesktop/UDisks2/block_devices/sdc1"
DISK_UUID = "d2f4a6c8-3b5e-4079-8a1c-6e9d2f4b7a30"
DISK_TEST_DATA = {
    "name": "test",
    "usage": "media",
    "type": "disk",
    "uuid": DISK_UUID,
    "filesystem": "ext4",
    "read_only": False,
}


@pytest.mark.parametrize(
    ("additional_data", "expected_options"),
    [
        (
            {"version": MountCifsVersion.LEGACY_1_0},
            ["vers=1.0"],
        ),
        (
            {"version": MountCifsVersion.LEGACY_2_0},
            ["vers=2.0"],
        ),
        (
            {"version": None},
            [],
        ),
    ],
)
async def test_cifs_mount(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data: Path,
    path_extern,
    additional_data: dict[str, Any],
    expected_options: list[str],
    mock_is_mount,
):
    """Test CIFS mount."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_unit_service: SystemdUnitService = all_dbus_services["systemd_unit"]
    systemd_service.StartTransientUnit.calls.clear()

    mount_data = {
        "name": "test",
        "usage": "backup",
        "type": "cifs",
        "server": "test.local",
        "share": "camera",
        "version": None,
        "username": "admin",
        "password": "password",
        "read_only": False,
        **additional_data,
    }
    mount: CIFSMount = Mount.from_dict(coresys, mount_data)

    assert isinstance(mount, CIFSMount)
    assert mount.name == "test"
    assert mount.type == MountType.CIFS
    assert mount.usage == MountUsage.BACKUP
    assert mount.port is None
    assert mount.state is None
    assert mount.unit is None
    assert mount.read_only is False

    assert mount.what == "//test.local/camera"
    assert mount.where == Path("/mnt/data/supervisor/mounts/test")
    assert mount.local_where == tmp_supervisor_data / "mounts" / "test"
    assert mount.options == [
        "noserverino",
        "soft",
        "echo_interval=10",
        "retrans=0",
    ] + expected_options + [
        "credentials=/mnt/data/supervisor/.mounts_credentials/test",
    ]

    assert not mount.local_where.exists()
    assert mount.to_dict(skip_secrets=False) == mount_data
    assert mount.to_dict() == {
        k: v for k, v in mount_data.items() if k not in ["username", "password"]
    }

    await mount.mount()

    assert mount.state == UnitActiveState.ACTIVE
    assert mount.local_where.exists()
    assert mount.local_where.is_dir()

    assert systemd_service.StartTransientUnit.calls == [
        mount_start_transient_unit_call(
            automount_unit="mnt-data-supervisor-mounts-test.automount",
            mount_unit="mnt-data-supervisor-mounts-test.mount",
            where="/mnt/data/supervisor/mounts/test",
            description="Supervisor cifs mount: test",
            what="//test.local/camera",
            fstype="cifs",
            options=",".join(
                ["noserverino", "soft", "echo_interval=10", "retrans=0"]
                + expected_options
                + ["credentials=/mnt/data/supervisor/.mounts_credentials/test"]
            ),
        )
    ]
    assert mount.path_credentials.exists()
    with mount.path_credentials.open("r") as creds:
        assert creds.read().split("\n") == [
            f"username={mount_data['username']}",
            f"password={mount_data['password']}",
        ]

    cred_stat = mount.path_credentials.stat()
    assert not cred_stat.st_mode & stat.S_IRGRP
    assert not cred_stat.st_mode & stat.S_IROTH

    systemd_unit_service.active_state = ["active", "inactive"]
    await mount.unmount()
    assert not mount.path_credentials.exists()


async def test_cifs_mount_read_only(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data: Path,
    path_extern,
    mock_is_mount,
):
    """Test a read-only cifs mount."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.StartTransientUnit.calls.clear()

    mount_data = {
        "name": "test",
        "usage": "backup",
        "type": "cifs",
        "server": "test.local",
        "share": "camera",
        "version": None,
        "read_only": True,
    }
    mount: CIFSMount = Mount.from_dict(coresys, mount_data)

    assert isinstance(mount, CIFSMount)
    assert mount.read_only is True

    await mount.mount()

    assert mount.state == UnitActiveState.ACTIVE
    assert mount.local_where.exists()
    assert mount.local_where.is_dir()

    assert systemd_service.StartTransientUnit.calls == [
        mount_start_transient_unit_call(
            automount_unit="mnt-data-supervisor-mounts-test.automount",
            mount_unit="mnt-data-supervisor-mounts-test.mount",
            where="/mnt/data/supervisor/mounts/test",
            description="Supervisor cifs mount: test",
            what="//test.local/camera",
            fstype="cifs",
            options="ro,noserverino,soft,echo_interval=10,retrans=0,guest",
        )
    ]


async def test_nfs_mount(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data: Path,
    path_extern,
    mock_is_mount,
):
    """Test NFS mount."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.StartTransientUnit.calls.clear()

    mount_data = {
        "name": "test",
        "usage": "backup",
        "type": "nfs",
        "server": "test.local",
        "path": "/media/camera",
        "port": 1234,
        "read_only": False,
    }
    mount: NFSMount = Mount.from_dict(coresys, mount_data)

    assert isinstance(mount, NFSMount)
    assert mount.name == "test"
    assert mount.type == MountType.NFS
    assert mount.usage == MountUsage.BACKUP
    assert mount.port == 1234
    assert mount.state is None
    assert mount.unit is None
    assert mount.read_only is False

    assert mount.what == "test.local:/media/camera"
    assert mount.where == Path("/mnt/data/supervisor/mounts/test")
    assert mount.local_where == tmp_supervisor_data / "mounts" / "test"
    assert mount.options == ["port=1234", "softerr", "timeo=100", "retrans=2"]

    assert not mount.local_where.exists()
    assert mount.to_dict() == mount_data

    await mount.mount()

    assert mount.state == UnitActiveState.ACTIVE
    assert mount.local_where.exists()
    assert mount.local_where.is_dir()

    assert systemd_service.StartTransientUnit.calls == [
        mount_start_transient_unit_call(
            automount_unit="mnt-data-supervisor-mounts-test.automount",
            mount_unit="mnt-data-supervisor-mounts-test.mount",
            where="/mnt/data/supervisor/mounts/test",
            description="Supervisor nfs mount: test",
            what="test.local:/media/camera",
            fstype="nfs",
            options="port=1234,softerr,timeo=100,retrans=2",
        )
    ]


async def test_nfs_mount_read_only(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data: Path,
    path_extern,
    mock_is_mount,
):
    """Test NFS mount."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.StartTransientUnit.calls.clear()

    mount_data = {
        "name": "test",
        "usage": "backup",
        "type": "nfs",
        "server": "test.local",
        "path": "/media/camera",
        "port": 1234,
        "read_only": True,
    }
    mount: NFSMount = Mount.from_dict(coresys, mount_data)

    assert isinstance(mount, NFSMount)
    assert mount.read_only is True

    await mount.mount()

    assert mount.state == UnitActiveState.ACTIVE
    assert mount.local_where.exists()
    assert mount.local_where.is_dir()

    assert systemd_service.StartTransientUnit.calls == [
        mount_start_transient_unit_call(
            automount_unit="mnt-data-supervisor-mounts-test.automount",
            mount_unit="mnt-data-supervisor-mounts-test.mount",
            where="/mnt/data/supervisor/mounts/test",
            description="Supervisor nfs mount: test",
            what="test.local:/media/camera",
            fstype="nfs",
            options="ro,port=1234,softerr,timeo=100,retrans=2",
        )
    ]


async def test_load(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    mock_is_mount,
):
    """Test mount loading."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_unit_service: SystemdUnitService = all_dbus_services["systemd_unit"]
    systemd_service.StartTransientUnit.calls.clear()
    systemd_service.ReloadOrRestartUnit.calls.clear()

    mount_data = {
        "name": "test",
        "usage": "backup",
        "type": "cifs",
        "server": "test.local",
        "share": "share",
    }

    # Load mounts it if the unit does not exist. Sequence: .mount lookup,
    # .automount lookup, then the post-mount refresh.
    systemd_service.response_get_unit = [
        ERROR_NO_UNIT,
        ERROR_NO_UNIT,
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount",
    ]
    mount = Mount.from_dict(coresys, mount_data)
    await mount.load()

    assert (
        mount.unit.object_path == "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount"
    )
    assert mount.state == UnitActiveState.ACTIVE
    assert systemd_service.StartTransientUnit.calls == [
        mount_start_transient_unit_call(
            automount_unit="mnt-data-supervisor-mounts-test.automount",
            mount_unit="mnt-data-supervisor-mounts-test.mount",
            where="/mnt/data/supervisor/mounts/test",
            description="Supervisor cifs mount: test",
            what="//test.local/share",
            fstype="cifs",
            options="noserverino,soft,echo_interval=10,retrans=0,guest",
        )
    ]
    assert systemd_service.ReloadOrRestartUnit.calls == []

    # Load does nothing except cache state and unit if it finds an active unit already
    systemd_service.StartTransientUnit.calls.clear()
    systemd_service.response_get_unit = (
        "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount"
    )
    mount = Mount.from_dict(coresys, mount_data)
    await mount.load()

    assert (
        mount.unit.object_path == "/org/freedesktop/systemd1/unit/tmp_2dyellow_2emount"
    )
    assert mount.state == UnitActiveState.ACTIVE
    assert systemd_service.StartTransientUnit.calls == []
    assert systemd_service.ReloadOrRestartUnit.calls == []

    # Load waits up to 30 seconds if it finds a unit in the activating
    # state — `_update_state_await` polls via PropertiesChanged until
    # the unit settles. The kernel's autofs trigger handles activation
    # from here on, so we don't reload/restart from `load()` anymore.
    # State reads: the .automount trigger is active (so the pair is
    # adopted), then the .mount is seen activating until the signal.
    systemd_unit_service.active_state = ["active", "activating"]
    mount = Mount.from_dict(coresys, mount_data)

    load_task = asyncio.create_task(mount.load())
    await asyncio.sleep(0.1)
    systemd_unit_service.emit_properties_changed({"ActiveState": "active"})
    await load_task

    assert mount.state == UnitActiveState.ACTIVE
    assert systemd_service.StartTransientUnit.calls == []
    assert systemd_service.ReloadOrRestartUnit.calls == []


async def test_load_rearms_failed_automount_trigger(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    mock_is_mount,
):
    """Test load re-arms the trigger instead of adopting a failed automount."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_unit_service: SystemdUnitService = all_dbus_services["systemd_unit"]
    systemd_service.StartTransientUnit.calls.clear()
    systemd_service.StopUnit.calls.clear()
    systemd_service.ResetFailedUnit.calls.clear()

    # State reads: the .automount trigger has failed (never adopt it —
    # the path would be a plain writable directory), the .mount is seen
    # failed as well during unmount (no stop job dispatched for it),
    # then the post-mount refresh reads active.
    systemd_unit_service.active_state = ["failed", "failed", "active"]

    mount = Mount.from_dict(
        coresys,
        {
            "name": "test",
            "usage": "backup",
            "type": "cifs",
            "server": "test.local",
            "share": "share",
        },
    )
    await mount.load()

    assert mount.state == UnitActiveState.ACTIVE
    assert systemd_service.StopUnit.calls == [
        ("mnt-data-supervisor-mounts-test.automount", "fail")
    ]
    assert [call[0] for call in systemd_service.ResetFailedUnit.calls] == [
        "mnt-data-supervisor-mounts-test.automount",
        "mnt-data-supervisor-mounts-test.mount",
    ]
    assert systemd_service.StartTransientUnit.calls == [
        mount_start_transient_unit_call(
            automount_unit="mnt-data-supervisor-mounts-test.automount",
            mount_unit="mnt-data-supervisor-mounts-test.mount",
            where="/mnt/data/supervisor/mounts/test",
            description="Supervisor cifs mount: test",
            what="//test.local/share",
            fstype="cifs",
            options="noserverino,soft,echo_interval=10,retrans=0,guest",
        )
    ]


async def test_load_adopted_mount_probe_failure(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
):
    """Test load raises when the adopted active pair fails the probe."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.StartTransientUnit.calls.clear()

    mount = Mount.from_dict(
        coresys,
        {
            "name": "test",
            "usage": "backup",
            "type": "cifs",
            "server": "test.local",
            "share": "share",
        },
    )

    # Both units exist and the .automount is active, but the server does
    # not answer the probe — an unreachable server is an error on adopt,
    # same as on a fresh mount.
    with (
        patch(
            "supervisor.mounts.mount._probe_mount",
            side_effect=OSError(errno.EHOSTDOWN, "Host is down"),
        ),
        pytest.raises(MountActivationError),
    ):
        await mount.load()

    assert systemd_service.StartTransientUnit.calls == []


async def test_unmount(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    path_extern,
    mock_is_mount,
):
    """Test unmounting."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_unit_service: SystemdUnitService = all_dbus_services["systemd_unit"]
    systemd_service.StopUnit.calls.clear()

    mount: CIFSMount = Mount.from_dict(
        coresys,
        {
            "name": "test",
            "usage": "backup",
            "type": "cifs",
            "server": "test.local",
            "share": "share",
        },
    )
    await mount.load()

    assert mount.unit is not None
    assert mount.state == UnitActiveState.ACTIVE

    systemd_unit_service.active_state = ["active", "inactive"]
    await mount.unmount()

    assert mount.unit is None
    assert mount.state is None
    # Network mount unmount stops the .automount companion first, then the
    # .mount itself.
    assert systemd_service.StopUnit.calls == [
        ("mnt-data-supervisor-mounts-test.automount", "fail"),
        ("mnt-data-supervisor-mounts-test.mount", "fail"),
    ]


async def test_mount_failure(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    mock_is_mount,
):
    """Test failure to mount."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_unit_service: SystemdUnitService = all_dbus_services["systemd_unit"]
    systemd_service.StartTransientUnit.calls.clear()
    systemd_service.GetUnit.calls.clear()

    mount = Mount.from_dict(
        coresys,
        {
            "name": "test",
            "usage": "backup",
            "type": "cifs",
            "server": "test.local",
            "share": "share",
        },
    )

    # Raise error on StartTransientUnit error
    systemd_service.response_start_transient_unit = ERROR_FAILURE
    with pytest.raises(MountSetupError):
        await mount.mount()

    assert mount.state is None
    assert len(systemd_service.StartTransientUnit.calls) == 1
    assert systemd_service.GetUnit.calls == []

    # Raise error if the post-mount probe fails. Under autofs the
    # systemd `.mount` is dormant until first access; the probe is
    # what proves the share actually works. Probe failure surfaces
    # as MountActivationError regardless of what systemd state says.
    systemd_service.StartTransientUnit.calls.clear()
    systemd_service.response_start_transient_unit = "/org/freedesktop/systemd1/job/7623"
    systemd_unit_service.active_state = "active"
    with (
        patch(
            "supervisor.mounts.mount._probe_mount",
            side_effect=OSError(errno.EHOSTDOWN, "Host is down"),
        ),
        pytest.raises(MountActivationError),
    ):
        await mount.mount()

    assert len(systemd_service.StartTransientUnit.calls) == 1


async def test_mount_arming_failure(
    coresys: CoreSys,
    tmp_supervisor_data,
    path_extern,
    mock_is_mount,
    caplog: pytest.LogCaptureFixture,
):
    """Test mount raises MountSetupError if the automount start job is not done."""
    mount = Mount.from_dict(
        coresys,
        {
            "name": "test",
            "usage": "backup",
            "type": "cifs",
            "server": "test.local",
            "share": "share",
        },
    )

    # A non-"done" start job result means the trigger never armed and the
    # path is a plain writable directory — a hard MountSetupError, distinct
    # from the armed-but-unreachable MountActivationError of the probe
    with (
        patch.object(Mount, "_run_systemd_job", return_value="failed") as run_job,
        pytest.raises(MountSetupError) as excinfo,
    ):
        await mount.mount()

    # Close the StartTransientUnit dispatch coroutine the mocked job
    # helper swallowed so it does not warn at garbage collection
    run_job.await_args.args[1].close()

    assert not isinstance(excinfo.value, MountActivationError)
    # The user-facing error is generic and translatable...
    assert (
        str(excinfo.value)
        == "Could not set up mount test. Check the Supervisor logs for details"
    )
    assert excinfo.value.error_key == "mount_setup_error"
    # ...while the technical detail stays in the log
    assert (
        "Could not arm automount for test (systemd job result: failed)" in caplog.text
    )


async def test_unmount_failure(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
):
    """Test failure to unmount."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.StopUnit.calls.clear()

    mount = Mount.from_dict(
        coresys,
        {
            "name": "test",
            "usage": "backup",
            "type": "cifs",
            "server": "test.local",
            "share": "share",
        },
    )

    # A failed .automount stop aborts the unmount before the .mount is
    # touched — continuing would leave an armed trigger behind at the
    # path of a supposedly removed mount.
    systemd_service.response_stop_unit = ERROR_FAILURE
    with pytest.raises(MountUnmountError):
        await mount.unmount()

    assert systemd_service.StopUnit.calls == [
        ("mnt-data-supervisor-mounts-test.automount", "fail")
    ]

    # With the .automount stopped the path is detached, so a failure
    # stopping the .mount raises but arms a fresh pair first — otherwise
    # the path stays a plain writable directory.
    systemd_service.StopUnit.calls.clear()
    systemd_service.StartTransientUnit.calls.clear()
    systemd_service.response_stop_unit = [
        "/org/freedesktop/systemd1/job/7623",
        ERROR_FAILURE,
    ]
    with (
        patch("supervisor.mounts.mount._probe_mount", return_value=True),
        pytest.raises(MountUnmountError),
    ):
        await mount.unmount()

    assert systemd_service.StopUnit.calls == [
        ("mnt-data-supervisor-mounts-test.automount", "fail"),
        ("mnt-data-supervisor-mounts-test.mount", "fail"),
    ]
    assert [call[0] for call in systemd_service.StartTransientUnit.calls] == [
        "mnt-data-supervisor-mounts-test.automount"
    ]

    # If the .mount unit is missing only the .automount stop is attempted —
    # it disarms the trigger and detaches anything left at the path.
    systemd_service.StopUnit.calls.clear()
    systemd_service.response_stop_unit = "/org/freedesktop/systemd1/job/7623"
    systemd_service.response_get_unit = ERROR_NO_UNIT
    await mount.unmount()
    assert systemd_service.StopUnit.calls == [
        ("mnt-data-supervisor-mounts-test.automount", "fail")
    ]


async def test_mount_local_where_invalid(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data: Path,
    path_extern,
):
    """Test mount errors because local where exists and is invalid."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.StartTransientUnit.calls.clear()

    mount = Mount.from_dict(
        coresys,
        {
            "name": "test",
            "usage": "backup",
            "type": "cifs",
            "server": "test.local",
            "share": "share",
        },
    )

    mount_path = tmp_supervisor_data / "mounts" / "test"
    assert not mount_path.exists()

    # Cannot mount on top of a non-directory
    mount_path.touch()

    with pytest.raises(MountInvalidError):
        await mount.mount()

    # Cannot mount on top of a non-empty directory
    mount_path.unlink()
    mount_path.mkdir()
    (mount_path / "test").touch()

    with pytest.raises(MountInvalidError):
        await mount.mount()

    assert systemd_service.StartTransientUnit.calls == []


async def test_mount_fails_if_down(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data: Path,
    mock_is_mount: MagicMock,
    path_extern,
):
    """Test mount fails if system is down (probe fails after activation)."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.StartTransientUnit.calls.clear()

    mount_data = {
        "name": "test",
        "usage": "backup",
        "type": "nfs",
        "server": "test.local",
        "path": "/media/camera",
        "port": 1234,
        "read_only": False,
    }
    mount: NFSMount = Mount.from_dict(coresys, mount_data)

    with (
        patch(
            "supervisor.mounts.mount._probe_mount",
            side_effect=OSError(errno.EHOSTDOWN, "Host is down"),
        ),
        pytest.raises(MountActivationError),
    ):
        await mount.mount()

    # Probe failure leaves the cached state at INACTIVE — the systemd
    # unit may still be reported active by the mock but the supervisor
    # knows the share isn't reachable.
    assert mount.state == UnitActiveState.INACTIVE
    assert mount.local_where.exists()
    assert mount.local_where.is_dir()

    assert systemd_service.StartTransientUnit.calls == [
        mount_start_transient_unit_call(
            automount_unit="mnt-data-supervisor-mounts-test.automount",
            mount_unit="mnt-data-supervisor-mounts-test.mount",
            where="/mnt/data/supervisor/mounts/test",
            description="Supervisor nfs mount: test",
            what="test.local:/media/camera",
            fstype="nfs",
            options="port=1234,softerr,timeo=100,retrans=2",
        )
    ]


async def test_unmount_failure_arms_trigger_without_aux(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
):
    """Test the re-arm falls back to the trigger alone.

    Stopping the .mount is what failed, so its transient definition is
    still loaded and systemd rejects it as an aux unit. Arming the
    .automount on its own covers the path and fires that definition.
    """
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.StartTransientUnit.calls.clear()

    mount = Mount.from_dict(
        coresys,
        {
            "name": "test",
            "usage": "backup",
            "type": "cifs",
            "server": "test.local",
            "share": "share",
        },
    )

    # Automount stops fine, stopping the .mount fails
    systemd_service.response_stop_unit = [
        "/org/freedesktop/systemd1/job/7623",
        ERROR_FAILURE,
    ]
    # Re-creating the pair is rejected, arming the trigger alone works
    systemd_service.response_start_transient_unit = [
        ERROR_FAILURE,
        "/org/freedesktop/systemd1/job/7623",
    ]

    with pytest.raises(MountUnmountError):
        await mount.unmount()

    assert [
        (call[0], call[3]) for call in systemd_service.StartTransientUnit.calls
    ] == [
        (
            "mnt-data-supervisor-mounts-test.automount",
            [("mnt-data-supervisor-mounts-test.mount", ANY)],
        ),
        ("mnt-data-supervisor-mounts-test.automount", []),
    ]


async def test_unmount_failure_leaves_local_data_visible(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    caplog: pytest.LogCaptureFixture,
):
    """Test data written while the path was uncovered is not armed over.

    A trigger on top would hide it: reconciliation finds a healthy mount
    and relocate_local_data() skips mount points, so the move-local-data
    repair could never reach it.
    """
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.StartTransientUnit.calls.clear()

    mount = Mount.from_dict(
        coresys,
        {
            "name": "test",
            "usage": "backup",
            "type": "cifs",
            "server": "test.local",
            "share": "share",
        },
    )
    mount.local_where.mkdir(parents=True)
    (mount.local_where / "written_while_uncovered").touch()

    # Automount stops fine, stopping the .mount fails
    systemd_service.response_stop_unit = [
        "/org/freedesktop/systemd1/job/7623",
        ERROR_FAILURE,
    ]

    with pytest.raises(MountUnmountError):
        await mount.unmount()

    assert systemd_service.StartTransientUnit.calls == []
    assert (mount.local_where / "written_while_uncovered").exists()
    assert "Could not re-arm automount for test" in caplog.text


async def test_disk_mount(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data: Path,
    path_extern,
    mock_is_mount,
):
    """Test a disk mount restored from persisted configuration."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_unit_service: SystemdUnitService = all_dbus_services["systemd_unit"]
    udisks2_manager_service: UDisks2ManagerService = all_dbus_services[
        "udisks2_manager"
    ]
    systemd_service.StartTransientUnit.calls.clear()
    udisks2_manager_service.ResolveDevice.calls.clear()

    mount: DiskMount = Mount.from_dict(coresys, DISK_TEST_DATA)

    assert isinstance(mount, DiskMount)
    assert mount.name == "test"
    assert mount.type == MountType.DISK
    assert mount.usage == MountUsage.MEDIA
    assert mount.read_only is False
    assert mount.state is None
    assert mount.unit is None

    assert mount.device is None
    assert mount.uuid == DISK_UUID
    assert mount.filesystem == "ext4"
    # What= sits outside /dev so systemd creates no device-unit dependency
    assert mount.what == "/mnt/data/supervisor/.mounts_devices/test"
    # A media mount lives under the container-facing media dir
    assert mount.where == PurePath("/mnt/data/supervisor/media/test")
    assert mount.local_where == tmp_supervisor_data / "media" / "test"
    # A local disk brings no mount options of its own
    assert mount.options == []
    assert mount.fs_type == "ext4"

    assert not mount.local_where.exists()
    assert mount.to_dict() == DISK_TEST_DATA

    await mount.mount()

    assert mount.state == UnitActiveState.ACTIVE
    assert mount.local_where.exists()
    assert mount.local_where.is_dir()

    # The unit mounts this link, which points at the resolved by-uuid node
    assert mount.path_device_link.is_symlink()
    assert mount.path_device_link.readlink() == Path(f"/dev/disk/by-uuid/{DISK_UUID}")

    # Already knows its filesystem; the single call is the presence probe
    assert len(udisks2_manager_service.ResolveDevice.calls) == 1

    assert systemd_service.StartTransientUnit.calls == [
        mount_start_transient_unit_call(
            automount_unit="mnt-data-supervisor-media-test.automount",
            mount_unit="mnt-data-supervisor-media-test.mount",
            where="/mnt/data/supervisor/media/test",
            description="Supervisor disk mount: test",
            what="/mnt/data/supervisor/.mounts_devices/test",
            fstype="ext4",
            options=None,
        )
    ]

    systemd_unit_service.active_state = ["active", "inactive"]
    await mount.unmount()

    # Unlink the link we created. is_symlink() does not follow it.
    assert not mount.path_device_link.is_symlink()


async def test_disk_mount_read_only(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data: Path,
    path_extern,
    mock_is_mount,
):
    """Test a read-only disk mount."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.StartTransientUnit.calls.clear()

    mount: DiskMount = Mount.from_dict(coresys, DISK_TEST_DATA | {"read_only": True})

    assert mount.read_only is True
    assert mount.options == ["ro"]

    await mount.mount()

    assert mount.state == UnitActiveState.ACTIVE
    assert systemd_service.StartTransientUnit.calls == [
        mount_start_transient_unit_call(
            automount_unit="mnt-data-supervisor-media-test.automount",
            mount_unit="mnt-data-supervisor-media-test.mount",
            where="/mnt/data/supervisor/media/test",
            description="Supervisor disk mount: test",
            what="/mnt/data/supervisor/.mounts_devices/test",
            fstype="ext4",
            options="ro",
        )
    ]


async def test_disk_mount_ntfs_uses_kernel_driver(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data: Path,
    path_extern,
    mock_is_mount,
):
    """Test the probed ntfs signature is handed to systemd as ntfs3."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.StartTransientUnit.calls.clear()

    mount: DiskMount = Mount.from_dict(coresys, DISK_TEST_DATA | {"filesystem": "ntfs"})

    assert mount.filesystem == "ntfs"
    assert mount.fs_type == "ntfs3"
    assert mount.to_dict()["filesystem"] == "ntfs"

    await mount.mount()

    assert systemd_service.StartTransientUnit.calls == [
        mount_start_transient_unit_call(
            automount_unit="mnt-data-supervisor-media-test.automount",
            mount_unit="mnt-data-supervisor-media-test.mount",
            where="/mnt/data/supervisor/media/test",
            description="Supervisor disk mount: test",
            what="/mnt/data/supervisor/.mounts_devices/test",
            fstype="ntfs3",
            options=None,
        )
    ]


@pytest.mark.parametrize(
    ("probed_filesystem", "expected_unit_type"),
    [
        ("ext2", "ext4"),
        ("ext3", "ext4"),
        ("ext4", "ext4"),
        ("f2fs", "f2fs"),
        ("ntfs", "ntfs3"),
        ("vfat", "vfat"),
        ("exfat", "exfat"),
        ("btrfs", "btrfs"),
    ],
)
async def test_disk_mount_fs_type_mapping(
    coresys: CoreSys,
    probed_filesystem: str,
    expected_unit_type: str,
    mock_is_mount,
):
    """Test every supported filesystem maps to the driver that mounts it."""
    mount: DiskMount = Mount.from_dict(
        coresys, DISK_TEST_DATA | {"filesystem": probed_filesystem}
    )

    assert mount.filesystem == probed_filesystem
    assert mount.fs_type == expected_unit_type
    assert mount.to_dict()["filesystem"] == probed_filesystem


async def test_disk_mount_persisted_unsupported_filesystem(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data: Path,
    path_extern,
    mock_is_mount,
):
    """Test a persisted filesystem outside the allowlist is refused at mount time."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    udisks2_manager_service: UDisks2ManagerService = all_dbus_services[
        "udisks2_manager"
    ]
    systemd_service.StartTransientUnit.calls.clear()
    udisks2_manager_service.ResolveDevice.calls.clear()

    mount: DiskMount = Mount.from_dict(
        coresys, DISK_TEST_DATA | {"filesystem": "reiserfs"}
    )

    with pytest.raises(MountFilesystemNotSupportedError):
        await mount.mount()

    # Never handed to systemd, and not re-resolved
    assert systemd_service.StartTransientUnit.calls == []
    assert udisks2_manager_service.ResolveDevice.calls == []


async def test_disk_mount_without_udisks2(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data: Path,
    path_extern,
    mock_is_mount,
):
    """Test a host without UDisks2 reports a clear unsupported error."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.StartTransientUnit.calls.clear()

    mount: DiskMount = Mount.from_dict(
        coresys,
        {"name": "test", "usage": "media", "type": "disk", "device": "/dev/sdc1"},
    )

    with (
        patch.object(
            type(coresys.dbus.udisks2),
            "is_connected",
            new_callable=PropertyMock,
            return_value=False,
        ),
        pytest.raises(MountDisksNotSupportedError),
    ):
        await mount.mount()

    assert systemd_service.StartTransientUnit.calls == []


async def test_disk_mount_resolves_device_on_create(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data: Path,
    path_extern,
    sdc_candidate: DBusServiceMock,
    mock_is_mount,
):
    """Test creating a disk mount by device path resolves and persists the UUID."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    udisks2_manager_service: UDisks2ManagerService = all_dbus_services[
        "udisks2_manager"
    ]
    systemd_service.StartTransientUnit.calls.clear()
    udisks2_manager_service.ResolveDevice.calls.clear()
    udisks2_manager_service.resolved_devices = [SDC1_OBJECT_PATH]

    mount: DiskMount = Mount.from_dict(
        coresys,
        {"name": "test", "usage": "media", "type": "disk", "device": "/dev/sdc1"},
    )

    assert mount.device == "/dev/sdc1"
    assert mount.uuid is None
    assert mount.filesystem is None

    await mount.mount()

    # One call resolves the device; the second is the presence probe
    assert len(udisks2_manager_service.ResolveDevice.calls) == 2

    # Device path is dropped; UUID and filesystem are what get persisted
    assert mount.uuid == DISK_UUID
    assert mount.filesystem == "ext4"
    assert mount.device is None
    assert "device" not in mount.to_dict()
    assert mount.what == "/mnt/data/supervisor/.mounts_devices/test"

    assert systemd_service.StartTransientUnit.calls == [
        mount_start_transient_unit_call(
            automount_unit="mnt-data-supervisor-media-test.automount",
            mount_unit="mnt-data-supervisor-media-test.mount",
            where="/mnt/data/supervisor/media/test",
            description="Supervisor disk mount: test",
            what="/mnt/data/supervisor/.mounts_devices/test",
            fstype="ext4",
            options=None,
        )
    ]


async def test_disk_mount_resolves_when_adopting_existing_unit(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data: Path,
    path_extern,
    sdc_candidate: DBusServiceMock,
    mock_is_mount,
):
    """Test a disk mount still resolves when it adopts an existing unit.

    load() only mounts when there is no unit yet. Resolve in load so a
    persisted mount always has a uuid.
    """
    systemd_service: SystemdService = all_dbus_services["systemd"]
    udisks2_manager_service: UDisks2ManagerService = all_dbus_services[
        "udisks2_manager"
    ]
    systemd_service.StartTransientUnit.calls.clear()
    udisks2_manager_service.ResolveDevice.calls.clear()
    udisks2_manager_service.resolved_devices = [SDC1_OBJECT_PATH]

    mount: DiskMount = Mount.from_dict(
        coresys,
        {"name": "test", "usage": "media", "type": "disk", "device": "/dev/sdc1"},
    )

    # Default mock reports an already active unit for this path
    await mount.load()

    assert mount.state == UnitActiveState.ACTIVE
    assert systemd_service.StartTransientUnit.calls == []

    # One call resolves the device; the second is the presence probe
    assert len(udisks2_manager_service.ResolveDevice.calls) == 2
    assert mount.uuid == DISK_UUID
    assert mount.filesystem == "ext4"
    assert mount.device is None
    assert "uuid" in mount.to_dict()


async def test_disk_mount_device_not_found(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data: Path,
    path_extern,
    mock_is_mount,
):
    """Test mounting a disk that is not present fails before touching systemd."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    udisks2_manager_service: UDisks2ManagerService = all_dbus_services[
        "udisks2_manager"
    ]
    systemd_service.StartTransientUnit.calls.clear()
    udisks2_manager_service.resolved_devices = []

    mount: DiskMount = Mount.from_dict(
        coresys,
        {"name": "test", "usage": "media", "type": "disk", "device": "/dev/sdz9"},
    )

    with pytest.raises(MountDeviceNotFoundError):
        await mount.mount()

    assert systemd_service.StartTransientUnit.calls == []


async def test_disk_mount_without_identifier(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data: Path,
    path_extern,
    mock_is_mount,
):
    """Test a disk mount with neither a device nor a UUID fails cleanly."""
    mount = DiskMount(
        coresys,
        {"name": "test", "type": "disk", "usage": "media", "read_only": False},
    )

    # Nothing to hand systemd as Type= until the device is resolved
    with pytest.raises(MountInvalidError, match="no resolved filesystem"):
        _ = mount.fs_type

    with pytest.raises(MountInvalidError, match="neither a device nor a UUID"):
        await mount.mount()


async def test_disk_mount_resolve_dbus_error(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data: Path,
    path_extern,
    mock_is_mount,
):
    """Test a UDisks2 failure while resolving is reported as a mount error."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.StartTransientUnit.calls.clear()

    mount: DiskMount = Mount.from_dict(
        coresys,
        {"name": "test", "usage": "media", "type": "disk", "device": "/dev/sdc1"},
    )

    with (
        patch.object(
            coresys.dbus.udisks2,
            "resolve_device",
            side_effect=SupervisorDBusError("no reply"),
        ),
        pytest.raises(MountError, match="Could not resolve device for mount test"),
    ):
        await mount.mount()

    assert systemd_service.StartTransientUnit.calls == []


async def test_disk_mount_ambiguous_device(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data: Path,
    path_extern,
    sdc_candidate: DBusServiceMock,
    mock_is_mount,
):
    """Test a UUID matching several devices is refused rather than guessed at."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    udisks2_manager_service: UDisks2ManagerService = all_dbus_services[
        "udisks2_manager"
    ]
    systemd_service.StartTransientUnit.calls.clear()
    udisks2_manager_service.resolved_devices = [SDC1_OBJECT_PATH, SDB1_OBJECT_PATH]

    mount: DiskMount = Mount.from_dict(
        coresys,
        {"name": "test", "usage": "media", "type": "disk", "uuid": DISK_UUID},
    )

    with pytest.raises(MountInvalidError, match="matches 2 devices"):
        await mount.mount()

    assert systemd_service.StartTransientUnit.calls == []


async def test_disk_mount_write_protected(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data: Path,
    path_extern,
    sdc_candidate: DBusServiceMock,
    mock_is_mount,
):
    """Test a write-protected disk is not silently downgraded to read-only."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    udisks2_manager_service: UDisks2ManagerService = all_dbus_services[
        "udisks2_manager"
    ]
    systemd_service.StartTransientUnit.calls.clear()
    udisks2_manager_service.resolved_devices = [SDC1_OBJECT_PATH]
    sdc_candidate.fixture = replace(sdc_candidate.fixture, ReadOnly=True)

    writable: DiskMount = Mount.from_dict(
        coresys,
        {"name": "test_rw", "usage": "media", "type": "disk", "device": "/dev/sdc1"},
    )

    with pytest.raises(MountDeviceReadOnlyError):
        await writable.mount()

    assert systemd_service.StartTransientUnit.calls == []

    # Asking for read-only explicitly is accepted
    read_only: DiskMount = Mount.from_dict(
        coresys,
        {
            "name": "test_ro",
            "usage": "media",
            "type": "disk",
            "device": "/dev/sdc1",
            "read_only": True,
        },
    )

    await read_only.mount()

    assert read_only.state == UnitActiveState.ACTIVE
    assert len(systemd_service.StartTransientUnit.calls) == 1


async def test_disk_mount_rejects_system_device(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data: Path,
    path_extern,
    mock_is_mount,
):
    """Test creating a mount runs the same guard the candidate list uses."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    udisks2_manager_service: UDisks2ManagerService = all_dbus_services[
        "udisks2_manager"
    ]
    systemd_service.StartTransientUnit.calls.clear()
    # sda1 is a previous data disk, excluded by its label
    udisks2_manager_service.resolved_devices = [
        "/org/freedesktop/UDisks2/block_devices/sda1"
    ]

    mount: DiskMount = Mount.from_dict(
        coresys,
        {"name": "test", "usage": "media", "type": "disk", "device": "/dev/sda1"},
    )

    with pytest.raises(MountInvalidError):
        await mount.mount()

    assert systemd_service.StartTransientUnit.calls == []


async def test_disk_mount_device_link_avoids_device_dependency(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data: Path,
    path_extern,
    mock_is_mount,
):
    """Test the unit mounts a link outside /dev, not the by-uuid node itself.

    A What= under /dev makes systemd wait DefaultDeviceTimeoutSec (90 s) for
    an absent device. Keep What= outside /dev so that does not happen.
    """
    mount: DiskMount = Mount.from_dict(coresys, DISK_TEST_DATA)

    assert not mount.what.startswith("/dev/")
    assert mount.what == "/mnt/data/supervisor/.mounts_devices/test"

    await mount.mount()

    # Link still resolves to the by-uuid node
    assert mount.path_device_link.readlink() == Path(f"/dev/disk/by-uuid/{DISK_UUID}")


async def test_disk_mount_reports_inactive_when_device_detached(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data: Path,
    path_extern,
    mock_is_mount,
):
    """Test a disk pulled while mounted is not reported active.

    statvfs is cached for a local filesystem, so only a UDisks2 presence
    check can tell a healthy disk from one that was unplugged.
    """
    udisks2_manager_service: UDisks2ManagerService = all_dbus_services[
        "udisks2_manager"
    ]
    mount: DiskMount = Mount.from_dict(coresys, DISK_TEST_DATA)
    await mount.mount()
    assert mount.state == UnitActiveState.ACTIVE

    # Probe still succeeds; only the device is gone
    udisks2_manager_service.resolved_devices = []

    assert await mount.is_mounted() is False
    assert mount.state == UnitActiveState.INACTIVE


async def test_disk_mount_stays_active_when_udisks2_unavailable(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data: Path,
    path_extern,
    mock_is_mount,
):
    """Test an unavailable UDisks2 is not treated as a missing disk."""
    mount: DiskMount = Mount.from_dict(coresys, DISK_TEST_DATA)
    await mount.mount()

    udisks2_manager_service: UDisks2ManagerService = all_dbus_services[
        "udisks2_manager"
    ]
    # Empty resolve would look like a missing disk without the is_connected guard
    udisks2_manager_service.resolved_devices = []

    with patch.object(
        type(coresys.dbus.udisks2), "is_connected", new_callable=PropertyMock
    ) as is_connected:
        is_connected.return_value = False
        assert await mount.is_mounted() is True

    assert mount.state == UnitActiveState.ACTIVE
