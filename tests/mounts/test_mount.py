"""Tests for mounts."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
import stat
from typing import Any
from unittest.mock import MagicMock

from dbus_fast import DBusError, ErrorType, Variant
import pytest

from supervisor.coresys import CoreSys
from supervisor.dbus.const import UnitActiveState
from supervisor.exceptions import MountActivationError, MountError, MountInvalidError
from supervisor.mounts.const import MountCifsVersion, MountType, MountUsage
from supervisor.mounts.mount import CIFSMount, Mount, NFSMount
from supervisor.resolution.const import ContextType, IssueType, SuggestionType

from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.systemd import Systemd as SystemdService
from tests.dbus_service_mocks.systemd_unit import SystemdUnit as SystemdUnitService

ERROR_FAILURE = DBusError(ErrorType.FAILED, "error")
ERROR_NO_UNIT = DBusError("org.freedesktop.systemd1.NoSuchUnit", "error")


@pytest.mark.parametrize(
    "additional_data,expected_options",
    (
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
    ),
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
        "usage": "media",
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
    assert mount.usage == MountUsage.MEDIA
    assert mount.port is None
    assert mount.state is None
    assert mount.unit is None
    assert mount.read_only is False

    assert mount.what == "//test.local/camera"
    assert mount.where == Path("/mnt/data/supervisor/mounts/test")
    assert mount.local_where == tmp_supervisor_data / "mounts" / "test"
    assert mount.options == ["noserverino"] + expected_options + [
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
        (
            "mnt-data-supervisor-mounts-test.mount",
            "fail",
            [
                [
                    "Options",
                    Variant(
                        "s",
                        ",".join(
                            ["noserverino"]
                            + expected_options
                            + [
                                "credentials=/mnt/data/supervisor/.mounts_credentials/test"
                            ]
                        ),
                    ),
                ],
                ["Type", Variant("s", "cifs")],
                ["Description", Variant("s", "Supervisor cifs mount: test")],
                ["What", Variant("s", "//test.local/camera")],
            ],
            [],
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
        "usage": "media",
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
        (
            "mnt-data-supervisor-mounts-test.mount",
            "fail",
            [
                ["Options", Variant("s", "ro,noserverino,guest")],
                ["Type", Variant("s", "cifs")],
                ["Description", Variant("s", "Supervisor cifs mount: test")],
                ["What", Variant("s", "//test.local/camera")],
            ],
            [],
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
        "usage": "media",
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
    assert mount.usage == MountUsage.MEDIA
    assert mount.port == 1234
    assert mount.state is None
    assert mount.unit is None
    assert mount.read_only is False

    assert mount.what == "test.local:/media/camera"
    assert mount.where == Path("/mnt/data/supervisor/mounts/test")
    assert mount.local_where == tmp_supervisor_data / "mounts" / "test"
    assert mount.options == ["port=1234", "soft", "timeo=200"]

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
                ["Options", Variant("s", "port=1234,soft,timeo=200")],
                ["Type", Variant("s", "nfs")],
                ["Description", Variant("s", "Supervisor nfs mount: test")],
                ["What", Variant("s", "test.local:/media/camera")],
            ],
            [],
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
        "usage": "media",
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
        (
            "mnt-data-supervisor-mounts-test.mount",
            "fail",
            [
                ["Options", Variant("s", "ro,port=1234,soft,timeo=200")],
                ["Type", Variant("s", "nfs")],
                ["Description", Variant("s", "Supervisor nfs mount: test")],
                ["What", Variant("s", "test.local:/media/camera")],
            ],
            [],
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
                ["Options", Variant("s", "noserverino,guest")],
                ["Type", Variant("s", "cifs")],
                ["Description", Variant("s", "Supervisor cifs mount: test")],
                ["What", Variant("s", "//test.local/share")],
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

    load_task = asyncio.create_task(mount.load())
    await asyncio.sleep(0.1)
    systemd_unit_service.emit_properties_changed({"ActiveState": "failed"})
    await asyncio.sleep(0.1)
    systemd_unit_service.emit_properties_changed({"ActiveState": "active"})
    await load_task

    assert mount.state == UnitActiveState.ACTIVE
    assert systemd_service.StartTransientUnit.calls == []
    assert systemd_service.ReloadOrRestartUnit.calls == [
        ("mnt-data-supervisor-mounts-test.mount", "fail")
    ]


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
            "usage": "media",
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
    assert systemd_service.StopUnit.calls == [
        ("mnt-data-supervisor-mounts-test.mount", "fail")
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

    load_task = asyncio.create_task(mount.mount())
    await asyncio.sleep(0.1)
    systemd_unit_service.emit_properties_changed({"ActiveState": "failed"})
    with pytest.raises(MountError):
        await load_task

    assert mount.state == UnitActiveState.FAILED
    assert len(systemd_service.StartTransientUnit.calls) == 1
    assert len(systemd_service.GetUnit.calls) == 1


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

    # If unit is missing we skip unmounting, its already gone
    systemd_service.StopUnit.calls.clear()
    systemd_service.response_get_unit = ERROR_NO_UNIT
    await mount.unmount()
    assert systemd_service.StopUnit.calls == []


async def test_reload_failure(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data,
    path_extern,
    mock_is_mount,
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


async def test_update_clears_issue(coresys: CoreSys, path_extern, mock_is_mount):
    """Test updating mount data clears corresponding failed mount issue if active."""
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

    assert mount.failed_issue not in coresys.resolution.issues

    coresys.resolution.create_issue(
        IssueType.MOUNT_FAILED,
        ContextType.MOUNT,
        reference="test",
        suggestions=[SuggestionType.EXECUTE_RELOAD, SuggestionType.EXECUTE_REMOVE],
    )

    assert mount.failed_issue in coresys.resolution.issues
    assert len(coresys.resolution.suggestions_for_issue(mount.failed_issue)) == 2

    assert await mount.update() is True

    assert mount.state == UnitActiveState.ACTIVE
    assert mount.failed_issue not in coresys.resolution.issues
    assert not coresys.resolution.suggestions_for_issue(mount.failed_issue)


async def test_update_leaves_issue_if_down(
    coresys: CoreSys, mock_is_mount: MagicMock, path_extern
):
    """Test issue is left if system is down after update (is_mount is false)."""
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

    assert mount.failed_issue not in coresys.resolution.issues

    coresys.resolution.create_issue(
        IssueType.MOUNT_FAILED,
        ContextType.MOUNT,
        reference="test",
        suggestions=[SuggestionType.EXECUTE_RELOAD, SuggestionType.EXECUTE_REMOVE],
    )

    assert mount.failed_issue in coresys.resolution.issues
    assert len(coresys.resolution.suggestions_for_issue(mount.failed_issue)) == 2

    mock_is_mount.return_value = False
    assert (await mount.update()) is False

    assert mount.state == UnitActiveState.ACTIVE
    assert mount.failed_issue in coresys.resolution.issues
    assert len(coresys.resolution.suggestions_for_issue(mount.failed_issue)) == 2


async def test_mount_fails_if_down(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data: Path,
    mock_is_mount: MagicMock,
    path_extern,
):
    """Test mount fails if system is down (is_mount is false)."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.StartTransientUnit.calls.clear()

    mount_data = {
        "name": "test",
        "usage": "media",
        "type": "nfs",
        "server": "test.local",
        "path": "/media/camera",
        "port": 1234,
        "read_only": False,
    }
    mount: NFSMount = Mount.from_dict(coresys, mount_data)

    mock_is_mount.return_value = False
    with pytest.raises(MountActivationError):
        await mount.mount()

    assert mount.state == UnitActiveState.ACTIVE
    assert mount.local_where.exists()
    assert mount.local_where.is_dir()

    assert systemd_service.StartTransientUnit.calls == [
        (
            "mnt-data-supervisor-mounts-test.mount",
            "fail",
            [
                ["Options", Variant("s", "port=1234,soft,timeo=200")],
                ["Type", Variant("s", "nfs")],
                ["Description", Variant("s", "Supervisor nfs mount: test")],
                ["What", Variant("s", "test.local:/media/camera")],
            ],
            [],
        )
    ]
