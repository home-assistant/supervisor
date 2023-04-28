"""Tests for mounts."""

import os
from pathlib import Path
from unittest.mock import patch

from dbus_fast import DBusError, ErrorType, Variant
import pytest

from supervisor.coresys import CoreSys
from supervisor.dbus.const import UnitActiveState
from supervisor.exceptions import MountError, MountInvalidError
from supervisor.mounts.const import MountType, MountUsage
from supervisor.mounts.mount import CIFSMount, Mount, NFSMount

from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.systemd import Systemd as SystemdService
from tests.dbus_service_mocks.systemd_unit import SystemdUnit as SystemdUnitService

ERROR_FAILURE = DBusError(ErrorType.FAILED, "error")
ERROR_NO_UNIT = DBusError("org.freedesktop.systemd1.NoSuchUnit", "error")


async def test_cifs_mount(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data: Path,
    path_extern,
):
    """Test CIFS mount."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.StartTransientUnit.calls.clear()

    mount_data = {
        "name": "test",
        "usage": "media",
        "type": "cifs",
        "server": "test.local",
        "share": "camera",
        "username": "admin",
        "password": "password",
    }
    mount: CIFSMount = Mount.from_dict(coresys, mount_data)

    assert isinstance(mount, CIFSMount)
    assert mount.name == "test"
    assert mount.type == MountType.CIFS
    assert mount.usage == MountUsage.MEDIA
    assert mount.port is None
    assert mount.state is None
    assert mount.unit is None

    assert mount.what == "//test.local/camera"
    assert mount.where == Path("/mnt/data/supervisor/mounts/test")
    assert mount.local_where == tmp_supervisor_data / "mounts" / "test"
    assert mount.options == ["username=admin", "password=password"]

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
        (
            "mnt-data-supervisor-mounts-test.mount",
            "fail",
            [
                ["Options", Variant("s", "username=admin,password=password")],
                ["Description", Variant("s", "Supervisor cifs mount: test")],
                ["What", Variant("s", "//test.local/camera")],
                ["Type", Variant("s", "cifs")],
            ],
            [],
        )
    ]


async def test_nfs_mount(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data: Path,
    path_extern,
):
    """Test NFS mount."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.StartTransientUnit.calls.clear()

    mount_data = {
        "name": "test",
        "usage": "media",
        "type": "nfs",
        "server": "test.local",
        "path": "/media/camera",
        "port": 1234,
    }
    mount: NFSMount = Mount.from_dict(coresys, mount_data)

    assert isinstance(mount, NFSMount)
    assert mount.name == "test"
    assert mount.type == MountType.NFS
    assert mount.usage == MountUsage.MEDIA
    assert mount.port == 1234
    assert mount.state is None
    assert mount.unit is None

    assert mount.what == "test.local:/media/camera"
    assert mount.where == Path("/mnt/data/supervisor/mounts/test")
    assert mount.local_where == tmp_supervisor_data / "mounts" / "test"
    assert mount.options == ["port=1234"]

    assert not mount.local_where.exists()
    assert mount.to_dict() == mount_data

    await mount.mount()

    assert mount.state == UnitActiveState.ACTIVE
    assert mount.local_where.exists()
    assert mount.local_where.is_dir()

    assert systemd_service.StartTransientUnit.calls == [
        (
            "mnt-data-supervisor-mounts-test.mount",
            "fail",
            [
                ["Options", Variant("s", "port=1234")],
                ["Description", Variant("s", "Supervisor nfs mount: test")],
                ["What", Variant("s", "test.local:/media/camera")],
                ["Type", Variant("s", "nfs")],
            ],
            [],
        )
    ]


async def test_load(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
):
    """Test mount loading."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_unit_service: SystemdUnitService = all_dbus_services["systemd_unit"]
    systemd_service.StartTransientUnit.calls.clear()
    systemd_service.ReloadOrRestartUnit.calls.clear()

    mount_data = {
        "name": "test",
        "usage": "media",
        "type": "cifs",
        "server": "test.local",
        "share": "share",
    }

    # Load mounts it if the unit does not exist
    systemd_service.response_get_unit = [
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
        (
            "mnt-data-supervisor-mounts-test.mount",
            "fail",
            [
                ["Description", Variant("s", "Supervisor cifs mount: test")],
                ["What", Variant("s", "//test.local/share")],
                ["Type", Variant("s", "cifs")],
            ],
            [],
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

    # Load restarts the unit if it finds it in a failed state
    systemd_unit_service.active_state = ["failed", "active"]
    mount = Mount.from_dict(coresys, mount_data)
    await mount.load()

    assert mount.state == UnitActiveState.ACTIVE
    assert systemd_service.StartTransientUnit.calls == []
    assert systemd_service.ReloadOrRestartUnit.calls == [
        ("mnt-data-supervisor-mounts-test.mount", "fail")
    ]

    # Load waits up to 30 seconds if it finds a unit in the activating state
    systemd_service.ReloadOrRestartUnit.calls.clear()
    systemd_unit_service.active_state = "activating"
    mount = Mount.from_dict(coresys, mount_data)

    async def mock_activation_finished(*_):
        assert mount.state == UnitActiveState.ACTIVATING
        assert systemd_service.ReloadOrRestartUnit.calls == []
        systemd_unit_service.active_state = ["failed", "active"]

    with patch("supervisor.mounts.mount.asyncio.sleep", new=mock_activation_finished):
        await mount.load()

    assert mount.state == UnitActiveState.ACTIVE
    assert systemd_service.StartTransientUnit.calls == []
    assert systemd_service.ReloadOrRestartUnit.calls == [
        ("mnt-data-supervisor-mounts-test.mount", "fail")
    ]


async def test_unmount(
    coresys: CoreSys, all_dbus_services: dict[str, DBusServiceMock], path_extern
):
    """Test unmounting."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.StopUnit.calls.clear()

    mount = Mount.from_dict(
        coresys,
        {
            "name": "test",
            "usage": "media",
            "type": "cifs",
            "server": "test.local",
            "share": "share",
        },
    )
    await mount.load()

    assert mount.unit is not None
    assert mount.state == UnitActiveState.ACTIVE

    await mount.unmount()

    assert mount.unit is None
    assert mount.state is None
    assert systemd_service.StopUnit.calls == [
        ("mnt-data-supervisor-mounts-test.mount", "fail")
    ]


async def test_mount_failure(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
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
            "usage": "media",
            "type": "cifs",
            "server": "test.local",
            "share": "share",
        },
    )

    # Raise error on StartTransientUnit error
    systemd_service.response_start_transient_unit = ERROR_FAILURE
    with pytest.raises(MountError):
        await mount.mount()

    assert mount.state is None
    assert len(systemd_service.StartTransientUnit.calls) == 1
    assert systemd_service.GetUnit.calls == []

    # Raise error if state is not "active" after mount
    systemd_service.StartTransientUnit.calls.clear()
    systemd_service.response_start_transient_unit = "/org/freedesktop/systemd1/job/7623"
    systemd_unit_service.active_state = "failed"
    with pytest.raises(MountError):
        await mount.mount()

    assert mount.state == UnitActiveState.FAILED
    assert len(systemd_service.StartTransientUnit.calls) == 1
    assert len(systemd_service.GetUnit.calls) == 1

    # If state is 'activating', wait it out and raise error if it does not become 'active'
    systemd_service.StartTransientUnit.calls.clear()
    systemd_service.GetUnit.calls.clear()
    systemd_unit_service.active_state = "activating"

    async def mock_activation_finished(*_):
        assert mount.state == UnitActiveState.ACTIVATING
        systemd_unit_service.active_state = "failed"

    with patch(
        "supervisor.mounts.mount.asyncio.sleep", new=mock_activation_finished
    ), pytest.raises(MountError):
        await mount.mount()

    assert mount.state == UnitActiveState.FAILED
    assert len(systemd_service.StartTransientUnit.calls) == 1
    assert len(systemd_service.GetUnit.calls) == 2


async def test_unmount_failure(
    coresys: CoreSys, all_dbus_services: dict[str, DBusServiceMock], path_extern
):
    """Test failure to unmount."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.StopUnit.calls.clear()

    mount = Mount.from_dict(
        coresys,
        {
            "name": "test",
            "usage": "media",
            "type": "cifs",
            "server": "test.local",
            "share": "share",
        },
    )

    # Raise error on StopUnit failure
    systemd_service.response_stop_unit = ERROR_FAILURE
    with pytest.raises(MountError):
        await mount.unmount()

    assert len(systemd_service.StopUnit.calls) == 1

    # If error is NoSuchUnit then ignore, it has already been unmounted
    systemd_service.StopUnit.calls.clear()
    systemd_service.response_stop_unit = ERROR_NO_UNIT
    await mount.unmount()
    assert len(systemd_service.StopUnit.calls) == 1


async def test_reload_failure(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
):
    """Test failure to reload."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_unit_service: SystemdUnitService = all_dbus_services["systemd_unit"]
    systemd_service.StartTransientUnit.calls.clear()
    systemd_service.ReloadOrRestartUnit.calls.clear()
    systemd_service.GetUnit.calls.clear()

    mount = Mount.from_dict(
        coresys,
        {
            "name": "test",
            "usage": "media",
            "type": "cifs",
            "server": "test.local",
            "share": "share",
        },
    )

    # Raise error on ReloadOrRestartUnit error
    systemd_service.response_reload_or_restart_unit = ERROR_FAILURE
    with pytest.raises(MountError):
        await mount.reload()

    assert mount.state is None
    assert len(systemd_service.ReloadOrRestartUnit.calls) == 1
    assert systemd_service.GetUnit.calls == []
    assert systemd_service.StartTransientUnit.calls == []

    # Raise error if state is not "active" after reload
    systemd_service.ReloadOrRestartUnit.calls.clear()
    systemd_service.response_reload_or_restart_unit = (
        "/org/freedesktop/systemd1/job/7623"
    )
    systemd_unit_service.active_state = "failed"
    with pytest.raises(MountError):
        await mount.reload()

    assert mount.state == UnitActiveState.FAILED
    assert len(systemd_service.ReloadOrRestartUnit.calls) == 1
    assert len(systemd_service.GetUnit.calls) == 1
    assert systemd_service.StartTransientUnit.calls == []

    # If error is NoSuchUnit then don't raise just mount instead as its not mounted
    systemd_service.ReloadOrRestartUnit.calls.clear()
    systemd_service.GetUnit.calls.clear()
    systemd_service.response_reload_or_restart_unit = ERROR_NO_UNIT
    systemd_unit_service.active_state = "active"

    await mount.reload()

    assert mount.state == UnitActiveState.ACTIVE
    assert len(systemd_service.ReloadOrRestartUnit.calls) == 1
    assert len(systemd_service.StartTransientUnit.calls) == 1
    assert len(systemd_service.GetUnit.calls) == 1


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
            "usage": "media",
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
    os.remove(mount_path)
    mount_path.mkdir()
    (mount_path / "test").touch()

    with pytest.raises(MountInvalidError):
        await mount.mount()

    assert systemd_service.StartTransientUnit.calls == []
