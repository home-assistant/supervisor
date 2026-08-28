"""Tests for mounts."""

from __future__ import annotations

import asyncio
import errno
from pathlib import Path
import stat
from typing import Any
from unittest.mock import ANY, MagicMock, patch

from dbus_fast import DBusError, ErrorType
import pytest

from supervisor.coresys import CoreSys
from supervisor.dbus.const import UnitActiveState
from supervisor.exceptions import (
    MountActivationError,
    MountInvalidError,
    MountSetupError,
    MountUnmountError,
)
from supervisor.mounts.const import MountCifsVersion, MountType, MountUsage
from supervisor.mounts.mount import CIFSMount, Mount, NFSMount

from tests.common import mount_start_transient_unit_call
from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.systemd import Systemd as SystemdService
from tests.dbus_service_mocks.systemd_unit import SystemdUnit as SystemdUnitService

ERROR_FAILURE = DBusError(ErrorType.FAILED, "error")
ERROR_NO_UNIT = DBusError("org.freedesktop.systemd1.NoSuchUnit", "error")


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
            "supervisor.mounts.mount._probe_network_mount",
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
            "supervisor.mounts.mount._probe_network_mount",
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
        patch("supervisor.mounts.mount._probe_network_mount", return_value=True),
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
            "supervisor.mounts.mount._probe_network_mount",
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
