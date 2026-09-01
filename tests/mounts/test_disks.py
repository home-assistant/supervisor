"""Tests for the shared local disk mount guard."""

from dataclasses import replace
from pathlib import Path
from unittest.mock import PropertyMock, patch

import pytest

from supervisor.coresys import CoreSys
from supervisor.exceptions import (
    MountDeviceInUseError,
    MountDeviceMissingUUIDError,
    MountDeviceProtectedError,
    MountFilesystemNotSupportedError,
    MountInvalidError,
)
from supervisor.mounts.const import SUPPORTED_LOCAL_FILESYSTEMS
from supervisor.mounts.disks import validate_block_for_mount

from tests.dbus_service_mocks.base import DBusServiceMock

SDA1_PATH = "/org/freedesktop/UDisks2/block_devices/sda1"
SDC1_PATH = "/org/freedesktop/UDisks2/block_devices/sdc1"
SDC1_UUID = "d2f4a6c8-3b5e-4079-8a1c-6e9d2f4b7a30"


@pytest.mark.usefixtures("sdc_candidate")
async def test_guard_allows_unmounted_usb_partition(coresys: CoreSys):
    """Test a plain unmounted ext4 partition on a USB drive passes every guard.

    sdc1 is a user's own partition, not one of Home Assistant OS's: no system
    hint, no hassos label, no data disk partition name, and nothing mounted.
    """
    block = coresys.dbus.udisks2.get_block_device(SDC1_PATH)

    validate_block_for_mount(coresys, block, used_uuids=set())


@pytest.mark.parametrize(
    ("object_path", "expected_error"),
    [
        (
            "/org/freedesktop/UDisks2/block_devices/sda",
            MountFilesystemNotSupportedError,
        ),
        (
            "/org/freedesktop/UDisks2/block_devices/zram1",
            MountFilesystemNotSupportedError,
        ),
        (
            "/org/freedesktop/UDisks2/block_devices/mmcblk1p1",
            MountDeviceProtectedError,
        ),
        (SDA1_PATH, MountDeviceProtectedError),
        (
            "/org/freedesktop/UDisks2/block_devices/sdb1",
            MountDeviceInUseError,
        ),
    ],
    ids=[
        "whole-disk-has-no-filesystem",
        "zram-has-no-filesystem-signature",
        "hassos-boot-hinted-as-system",
        "hassos-data-old-despite-hint-system-false",
        "already-mounted-at-media-ext",
    ],
)
async def test_guard_rails(
    coresys: CoreSys, object_path: str, expected_error: type[MountInvalidError]
):
    """Test each excluded device raises the error that explains why."""
    block = coresys.dbus.udisks2.get_block_device(object_path)

    with pytest.raises(expected_error):
        validate_block_for_mount(coresys, block, used_uuids=set())


async def test_guard_rejects_hidden_device(
    coresys: CoreSys, sdc_candidate: DBusServiceMock
):
    """Test a device UDisks2 asks us to hide is not offered."""
    sdc_candidate.fixture = replace(sdc_candidate.fixture, HintIgnore=True)
    await coresys.dbus.udisks2.update()

    with pytest.raises(MountDeviceProtectedError):
        validate_block_for_mount(
            coresys, coresys.dbus.udisks2.get_block_device(SDC1_PATH), used_uuids=set()
        )


async def test_guard_rejects_hassos_label(
    coresys: CoreSys, sdc_candidate: DBusServiceMock
):
    """Test a disk carrying a Home Assistant OS filesystem label is not offered.

    This guard carries its own weight: a previous data disk is labelled
    hassos-data-old and reports HintSystem=False, so on a plain USB partition
    nothing else would exclude it. Tested here on sdc1 rather than sda1
    because sda1 is also caught by the external data disk partition name
    behind this check.
    """
    sdc_candidate.fixture = replace(sdc_candidate.fixture, IdLabel="hassos-data-old")
    await coresys.dbus.udisks2.update()

    with pytest.raises(MountDeviceProtectedError):
        validate_block_for_mount(
            coresys, coresys.dbus.udisks2.get_block_device(SDC1_PATH), used_uuids=set()
        )


@pytest.mark.parametrize(
    "filesystem", ["btrfs", "exfat", "ext2", "ext3", "ext4", "f2fs", "ntfs", "vfat"]
)
async def test_guard_allows_every_supported_filesystem(
    coresys: CoreSys, sdc_candidate: DBusServiceMock, filesystem: str
):
    """Test each filesystem on the allowlist is offered as a candidate."""
    sdc_candidate.fixture = replace(sdc_candidate.fixture, IdType=filesystem)
    await coresys.dbus.udisks2.update()

    validate_block_for_mount(
        coresys, coresys.dbus.udisks2.get_block_device(SDC1_PATH), used_uuids=set()
    )


async def test_supported_filesystems_are_enumerated_by_tests():
    """Test the allowlist and the cases above cannot drift apart.

    The guard is what keeps a disk the kernel cannot mount, or one that is
    not the user's to mount, out of the candidates list, so widening it is a
    deliberate act that should not pass unnoticed.
    """
    enumerated_above = {
        "btrfs",
        "exfat",
        "ext2",
        "ext3",
        "ext4",
        "f2fs",
        "ntfs",
        "vfat",
    }

    assert enumerated_above == SUPPORTED_LOCAL_FILESYSTEMS


async def test_guard_rejects_unsupported_filesystem(
    coresys: CoreSys, sdc_candidate: DBusServiceMock
):
    """Test a filesystem the kernel cannot mount is rejected.

    Note this is deliberately independent of UDisks2's SupportedFilesystems,
    which reports what the host can format rather than what it can mount.
    """
    sdc_candidate.fixture = replace(sdc_candidate.fixture, IdType="reiserfs")
    await coresys.dbus.udisks2.update()

    with pytest.raises(MountFilesystemNotSupportedError):
        validate_block_for_mount(
            coresys, coresys.dbus.udisks2.get_block_device(SDC1_PATH), used_uuids=set()
        )


async def test_guard_rejects_missing_uuid(
    coresys: CoreSys, sdc_candidate: DBusServiceMock
):
    """Test a filesystem without a UUID is rejected, as there is nothing to persist."""
    sdc_candidate.fixture = replace(sdc_candidate.fixture, IdUUID="")
    await coresys.dbus.udisks2.update()

    with pytest.raises(MountDeviceMissingUUIDError):
        validate_block_for_mount(
            coresys, coresys.dbus.udisks2.get_block_device(SDC1_PATH), used_uuids=set()
        )


@pytest.mark.usefixtures("sdc_candidate")
async def test_guard_rejects_uuid_already_mounted_by_supervisor(coresys: CoreSys):
    """Test a disk already used by another supervisor mount is rejected."""
    block = coresys.dbus.udisks2.get_block_device(SDC1_PATH)

    with pytest.raises(MountDeviceInUseError):
        validate_block_for_mount(coresys, block, used_uuids={SDC1_UUID})


async def test_guard_rejects_external_data_disk_partition(
    coresys: CoreSys,
    udisks2_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
):
    """Test a partition named for an external data disk is rejected.

    sda1 is normally caught by its hassos filesystem label, so the label is
    relabelled here to isolate the partition name guard behind it.
    """
    sda1_block = udisks2_services["udisks2_block"][SDA1_PATH]
    sda1_block.fixture = replace(sda1_block.fixture, IdLabel="Photos")
    await coresys.dbus.udisks2.update()

    with pytest.raises(MountDeviceProtectedError):
        validate_block_for_mount(
            coresys, coresys.dbus.udisks2.get_block_device(SDA1_PATH), used_uuids=set()
        )


@pytest.mark.usefixtures("sdc_candidate")
async def test_guard_rejects_current_data_disk(coresys: CoreSys):
    """Test the data partition currently in use is never offered."""
    block = coresys.dbus.udisks2.get_block_device(SDC1_PATH)

    with (
        patch.object(
            type(coresys.dbus.agent.datadisk),
            "current_device",
            new_callable=PropertyMock,
            return_value=Path("/dev/sdc1"),
        ),
        pytest.raises(MountDeviceProtectedError),
    ):
        validate_block_for_mount(coresys, block, used_uuids=set())


@pytest.mark.usefixtures("sdc_candidate")
async def test_guard_without_os_agent(coresys: CoreSys):
    """Test the data disk guard is skipped where OS-Agent is absent.

    A supervised install has no managed data disk to protect.
    """
    block = coresys.dbus.udisks2.get_block_device(SDC1_PATH)

    with patch.object(
        type(coresys.dbus.agent.datadisk),
        "is_connected",
        new_callable=PropertyMock,
        return_value=False,
    ):
        validate_block_for_mount(coresys, block, used_uuids=set())
