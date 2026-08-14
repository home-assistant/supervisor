"""Tests for mounts."""

from __future__ import annotations

import asyncio
from dataclasses import replace
import errno
from pathlib import Path
import stat
from typing import Any
from unittest.mock import MagicMock, PropertyMock, patch

from dbus_fast import DBusError, ErrorType, Variant
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
)
from supervisor.mounts.const import MountCifsVersion, MountType, MountUsage
from supervisor.mounts.mount import CIFSMount, DiskMount, Mount, NFSMount
from supervisor.resolution.const import ContextType, IssueType, SuggestionType

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
        (
            "mnt-data-supervisor-mounts-test.mount",
            "fail",
            [
                (
                    "Options",
                    Variant(
                        "s",
                        ",".join(
                            [
                                "noserverino",
                                "soft",
                                "echo_interval=10",
                                "retrans=0",
                            ]
                            + expected_options
                            + [
                                "credentials=/mnt/data/supervisor/.mounts_credentials/test"
                            ]
                        ),
                    ),
                ),
                ("Type", Variant("s", "cifs")),
                ("Description", Variant("s", "Supervisor cifs mount: test")),
                ("What", Variant("s", "//test.local/camera")),
                ("TimeoutUSec", Variant("t", 35000000)),
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
                (
                    "Options",
                    Variant(
                        "s", "ro,noserverino,soft,echo_interval=10,retrans=0,guest"
                    ),
                ),
                ("Type", Variant("s", "cifs")),
                ("Description", Variant("s", "Supervisor cifs mount: test")),
                ("What", Variant("s", "//test.local/camera")),
                ("TimeoutUSec", Variant("t", 35000000)),
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
    assert mount.options == ["port=1234", "softerr", "timeo=100", "retrans=2"]

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
                ("Options", Variant("s", "port=1234,softerr,timeo=100,retrans=2")),
                ("Type", Variant("s", "nfs")),
                ("Description", Variant("s", "Supervisor nfs mount: test")),
                ("What", Variant("s", "test.local:/media/camera")),
                ("TimeoutUSec", Variant("t", 35000000)),
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
                ("Options", Variant("s", "ro,port=1234,softerr,timeo=100,retrans=2")),
                ("Type", Variant("s", "nfs")),
                ("Description", Variant("s", "Supervisor nfs mount: test")),
                ("What", Variant("s", "test.local:/media/camera")),
                ("TimeoutUSec", Variant("t", 35000000)),
            ],
            [],
        )
    ]


async def test_disk_mount(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data: Path,
    path_extern,
):
    """Test a disk mount restored from persisted configuration.

    Deliberately without `mock_is_mount`: a local disk has no server to
    probe, so it must rely on the inherited systemd-state check alone.
    """
    systemd_service: SystemdService = all_dbus_services["systemd"]
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
    assert mount.what == f"/dev/disk/by-uuid/{DISK_UUID}"
    assert mount.where == Path("/mnt/data/supervisor/mounts/test")
    assert mount.local_where == tmp_supervisor_data / "mounts" / "test"
    # A local disk brings no mount options of its own
    assert mount.options == []
    assert mount.unit_type == "ext4"

    assert not mount.local_where.exists()
    assert mount.to_dict() == DISK_TEST_DATA

    await mount.mount()

    assert mount.state == UnitActiveState.ACTIVE
    assert mount.local_where.exists()
    assert mount.local_where.is_dir()

    # Already knows its device, so no UDisks2 round trip on the way back up
    assert udisks2_manager_service.ResolveDevice.calls == []

    assert systemd_service.StartTransientUnit.calls == [
        (
            "mnt-data-supervisor-mounts-test.mount",
            "fail",
            [
                ("Type", Variant("s", "ext4")),
                ("Description", Variant("s", "Supervisor disk mount: test")),
                ("What", Variant("s", f"/dev/disk/by-uuid/{DISK_UUID}")),
                ("TimeoutUSec", Variant("t", 35000000)),
            ],
            [],
        )
    ]


async def test_disk_mount_read_only(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data: Path,
    path_extern,
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
        (
            "mnt-data-supervisor-mounts-test.mount",
            "fail",
            [
                ("Options", Variant("s", "ro")),
                ("Type", Variant("s", "ext4")),
                ("Description", Variant("s", "Supervisor disk mount: test")),
                ("What", Variant("s", f"/dev/disk/by-uuid/{DISK_UUID}")),
                ("TimeoutUSec", Variant("t", 35000000)),
            ],
            [],
        )
    ]


async def test_disk_mount_ntfs_uses_kernel_driver(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data: Path,
    path_extern,
):
    """Test the probed ntfs signature is handed to systemd as ntfs3.

    UDisks2 reports the on-disk signature; the kernel driver that mounts it
    has a different name. Only the unit is translated — what gets persisted
    and reported back stays the probed value.
    """
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_service.StartTransientUnit.calls.clear()

    mount: DiskMount = Mount.from_dict(coresys, DISK_TEST_DATA | {"filesystem": "ntfs"})

    assert mount.filesystem == "ntfs"
    assert mount.unit_type == "ntfs3"
    assert mount.to_dict()["filesystem"] == "ntfs"

    await mount.mount()

    assert systemd_service.StartTransientUnit.calls == [
        (
            "mnt-data-supervisor-mounts-test.mount",
            "fail",
            [
                ("Type", Variant("s", "ntfs3")),
                ("Description", Variant("s", "Supervisor disk mount: test")),
                ("What", Variant("s", f"/dev/disk/by-uuid/{DISK_UUID}")),
                ("TimeoutUSec", Variant("t", 35000000)),
            ],
            [],
        )
    ]


@pytest.mark.parametrize(
    ("probed_filesystem", "expected_unit_type"),
    [
        ("ext2", "ext4"),
        ("ext3", "ext4"),
        ("ext4", "ext4"),
        ("ntfs", "ntfs3"),
        ("vfat", "vfat"),
        ("exfat", "exfat"),
        ("btrfs", "btrfs"),
    ],
)
async def test_disk_mount_unit_type_mapping(
    coresys: CoreSys, probed_filesystem: str, expected_unit_type: str
):
    """Test every supported filesystem maps to the driver that mounts it.

    UDisks2 reports the on-disk signature. ext2 and ext3 are both mounted by
    the ext4 driver and ntfs by ntfs3; the rest are named the same either way.
    The probed value is always what gets persisted and reported.
    """
    mount: DiskMount = Mount.from_dict(
        coresys, DISK_TEST_DATA | {"filesystem": probed_filesystem}
    )

    assert mount.filesystem == probed_filesystem
    assert mount.unit_type == expected_unit_type
    assert mount.to_dict()["filesystem"] == probed_filesystem


async def test_disk_mount_persisted_unsupported_filesystem(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data: Path,
    path_extern,
):
    """Test a persisted filesystem outside the allowlist is refused at mount time.

    A mount loaded from configuration skips the candidate guard, so the
    allowlist is re-checked here. mounts.json may have been hand-edited, or
    restored from a backup taken on a supervisor that allowed more types.
    """
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

    # Never handed to systemd, and no attempt to re-resolve it either
    assert systemd_service.StartTransientUnit.calls == []
    assert udisks2_manager_service.ResolveDevice.calls == []


async def test_disk_mount_without_udisks2(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data: Path,
    path_extern,
):
    """Test a host without UDisks2 reports a clear unsupported error.

    `resolve_device` would otherwise raise DBusNotConnectedError, which is not
    a DBusError and would escape as an unexpected server error.
    """
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

    assert len(udisks2_manager_service.ResolveDevice.calls) == 1

    # The volatile device path is traded for stable identifiers and dropped,
    # so coming back after a reboot does not depend on the kernel handing out
    # /dev/sdc1 again.
    assert mount.uuid == DISK_UUID
    assert mount.filesystem == "ext4"
    assert mount.device is None
    assert "device" not in mount.to_dict()
    assert mount.what == f"/dev/disk/by-uuid/{DISK_UUID}"

    assert systemd_service.StartTransientUnit.calls == [
        (
            "mnt-data-supervisor-mounts-test.mount",
            "fail",
            [
                ("Type", Variant("s", "ext4")),
                ("Description", Variant("s", "Supervisor disk mount: test")),
                ("What", Variant("s", f"/dev/disk/by-uuid/{DISK_UUID}")),
                ("TimeoutUSec", Variant("t", 35000000)),
            ],
            [],
        )
    ]


async def test_disk_mount_resolves_when_adopting_existing_unit(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data: Path,
    path_extern,
    sdc_candidate: DBusServiceMock,
):
    """Test a disk mount still resolves when it adopts an existing unit.

    `load()` only mounts when there is no unit for the path yet. Resolving
    from `mount()` alone would leave a mount that adopted a live unit with no
    uuid — and `to_dict` would then persist a mount that cannot be loaded
    back, because the schema requires an identifier.
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

    # The default mock reports an already active unit for this path
    await mount.load()

    assert mount.state == UnitActiveState.ACTIVE
    assert systemd_service.StartTransientUnit.calls == []

    assert len(udisks2_manager_service.ResolveDevice.calls) == 1
    assert mount.uuid == DISK_UUID
    assert mount.filesystem == "ext4"
    assert mount.device is None
    assert "uuid" in mount.to_dict()


async def test_disk_mount_device_not_found(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data: Path,
    path_extern,
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
):
    """Test a disk mount with neither a device nor a UUID fails cleanly.

    Validation requires one of the two, so this only arises for a mount built
    in code or read back from a hand-edited configuration.
    """
    mount = DiskMount(
        coresys,
        {"name": "test", "type": "disk", "usage": "media", "read_only": False},
    )

    # Nothing to hand systemd as Type= either, until it is resolved
    assert mount.unit_type is None

    with pytest.raises(MountInvalidError, match="neither a device nor a UUID"):
        await mount.mount()


async def test_disk_mount_resolve_dbus_error(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock],
    tmp_supervisor_data: Path,
    path_extern,
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
):
    """Test creating a mount runs the same guard the candidate list uses."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    udisks2_manager_service: UDisks2ManagerService = all_dbus_services[
        "udisks2_manager"
    ]
    systemd_service.StartTransientUnit.calls.clear()
    # sda1 is a previous data disk, excluded from candidates by its label
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
                (
                    "Options",
                    Variant("s", "noserverino,soft,echo_interval=10,retrans=0,guest"),
                ),
                ("Type", Variant("s", "cifs")),
                ("Description", Variant("s", "Supervisor cifs mount: test")),
                ("What", Variant("s", "//test.local/share")),
                ("TimeoutUSec", Variant("t", 35000000)),
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
    # (the wait happens inside _update_state_await driven by PropertiesChanged).
    # Once the state settles to FAILED, load triggers a reload, and the reload
    # is driven to completion by the mock-emitted JobRemoved signal — which
    # also flips active_state to "active" via mock_systemd_unit.
    systemd_service.mock_systemd_unit = systemd_unit_service
    systemd_service.ReloadOrRestartUnit.calls.clear()
    systemd_unit_service.active_state = "activating"
    mount = Mount.from_dict(coresys, mount_data)

    load_task = asyncio.create_task(mount.load())
    await asyncio.sleep(0.1)
    systemd_unit_service.emit_properties_changed({"ActiveState": "failed"})
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

    # When the post-dispatch state is not 'active' the mount call raises.
    # With JobRemoved as the completion signal, supervisor trusts that the
    # job is done by the time the signal fires — the systemd-side state
    # await happens inside systemd, not in supervisor.
    systemd_service.StartTransientUnit.calls.clear()
    systemd_service.GetUnit.calls.clear()
    systemd_unit_service.active_state = "failed"
    with pytest.raises(MountError):
        await mount.mount()

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


@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern", "mock_is_mount")
async def test_reload_failure(
    coresys: CoreSys, all_dbus_services: dict[str, DBusServiceMock]
):
    """Test failure to reload."""
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_unit_service: SystemdUnitService = all_dbus_services["systemd_unit"]
    systemd_service.StartTransientUnit.calls.clear()
    systemd_service.ReloadOrRestartUnit.calls.clear()
    systemd_service.RestartUnit.calls.clear()
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

    # Raise error on ReloadOrRestartUnit and RestartUnit error
    systemd_service.response_reload_or_restart_unit = ERROR_FAILURE
    systemd_service.response_restart_unit = ERROR_FAILURE
    with pytest.raises(MountError):
        await mount.reload()

    assert mount.state is None
    assert len(systemd_service.ReloadOrRestartUnit.calls) == 1
    assert len(systemd_service.RestartUnit.calls) == 1
    assert systemd_service.GetUnit.calls == []
    assert systemd_service.StartTransientUnit.calls == []

    # RestartUnit if ReloadOrRestartUnit does not get it mounted
    systemd_service.ReloadOrRestartUnit.calls.clear()
    systemd_service.RestartUnit.calls.clear()
    systemd_service.response_reload_or_restart_unit = (
        "/org/freedesktop/systemd1/job/7623"
    )
    systemd_service.response_restart_unit = "/org/freedesktop/systemd1/job/7623"
    # Probe fails after reload (server still unreachable) but succeeds
    # after restart — exercises the reload -> restart escalation path.
    with patch(
        "supervisor.mounts.mount._probe_network_mount",
        side_effect=[OSError(errno.EHOSTDOWN, "Host is down"), True],
    ):
        await mount.reload()

    assert mount.state == UnitActiveState.ACTIVE
    assert len(systemd_service.ReloadOrRestartUnit.calls) == 1
    assert len(systemd_service.RestartUnit.calls) == 1
    assert len(systemd_service.GetUnit.calls) == 2
    assert systemd_service.StartTransientUnit.calls == []

    # Raise error if state is not "active" after reload
    systemd_service.ReloadOrRestartUnit.calls.clear()
    systemd_service.RestartUnit.calls.clear()
    systemd_service.GetUnit.calls.clear()
    systemd_unit_service.active_state = "failed"
    # Force the fast-path probe to fail so reload actually exercises the
    # reload -> restart escalation we're testing here.
    with (
        patch(
            "supervisor.mounts.mount._probe_network_mount",
            side_effect=OSError(errno.EHOSTDOWN, "Host is down"),
        ),
        pytest.raises(MountError),
    ):
        await mount.reload()

    assert mount.state == UnitActiveState.FAILED
    assert len(systemd_service.ReloadOrRestartUnit.calls) == 1
    assert len(systemd_service.RestartUnit.calls) == 1
    assert len(systemd_service.GetUnit.calls) == 2
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


@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern", "mock_is_mount")
async def test_reload_does_not_escalate_when_still_reloading(
    coresys: CoreSys, all_dbus_services: dict[str, DBusServiceMock]
):
    """If the reload helper is still pinned (unit stays RELOADING), do not call RestartUnit.

    Issuing RestartUnit while a mount/umount syscall is stuck in the kernel can
    wedge PID 1 long enough for the hardware watchdog to reset the host. See
    issue #6827.
    """
    systemd_service: SystemdService = all_dbus_services["systemd"]
    systemd_unit_service: SystemdUnitService = all_dbus_services["systemd_unit"]
    systemd_service.ReloadOrRestartUnit.calls.clear()
    systemd_service.RestartUnit.calls.clear()
    systemd_service.response_reload_or_restart_unit = (
        "/org/freedesktop/systemd1/job/7624"
    )
    systemd_unit_service.active_state = "reloading"

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

    # Simulate the state-await timing out without the unit leaving RELOADING:
    # the helper is pinned in the kernel and systemd has not yet completed the
    # reload job. The state-await is responsible for refreshing self._state in
    # this case, so we mirror that here.
    # pylint: disable=protected-access
    async def _fake_update_state_await(self, unit, expected_states=None):
        await self._update_state(unit)  # noqa: SLF001

    with (
        patch.object(Mount, "_update_state_await", _fake_update_state_await),
        pytest.raises(MountActivationError),
    ):
        await mount.reload()

    assert mount.state == UnitActiveState.RELOADING
    assert len(systemd_service.ReloadOrRestartUnit.calls) == 1
    assert systemd_service.RestartUnit.calls == []


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
    mount_path.unlink()
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
    """Test issue is left if system is down after update (probe fails)."""
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

    with patch(
        "supervisor.mounts.mount._probe_network_mount",
        side_effect=OSError(errno.EHOSTDOWN, "Host is down"),
    ):
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
    """Test mount fails if system is down (probe fails after activation)."""
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

    with (
        patch(
            "supervisor.mounts.mount._probe_network_mount",
            side_effect=OSError(errno.EHOSTDOWN, "Host is down"),
        ),
        pytest.raises(MountActivationError),
    ):
        await mount.mount()

    assert mount.state == UnitActiveState.ACTIVE
    assert mount.local_where.exists()
    assert mount.local_where.is_dir()

    assert systemd_service.StartTransientUnit.calls == [
        (
            "mnt-data-supervisor-mounts-test.mount",
            "fail",
            [
                ("Options", Variant("s", "port=1234,softerr,timeo=100,retrans=2")),
                ("Type", Variant("s", "nfs")),
                ("Description", Variant("s", "Supervisor nfs mount: test")),
                ("What", Variant("s", "test.local:/media/camera")),
                ("TimeoutUSec", Variant("t", 35000000)),
            ],
            [],
        )
    ]
