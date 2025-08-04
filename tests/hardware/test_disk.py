"""Test hardware utils."""

# pylint: disable=protected-access
from pathlib import Path
from unittest.mock import patch

from dbus_fast.aio import MessageBus
import pytest

from supervisor.coresys import CoreSys
from supervisor.hardware.data import Device

from tests.common import mock_dbus_services
from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.udisks2_manager import (
    UDisks2Manager as UDisks2ManagerService,
)
from tests.dbus_service_mocks.udisks2_nvme_controller import (
    NVMeController as NVMeControllerService,
)

MOCK_MOUNTINFO = """790 750 259:8 /supervisor /data rw,relatime master:118 - ext4 /dev/nvme0n1p8 rw,commit=30
810 750 0:24 /systemd-journal-gatewayd.sock /run/systemd-journal-gatewayd.sock rw,nosuid,nodev - tmpfs tmpfs rw,size=405464k,nr_inodes=819200,mode=755
811 750 0:24 /supervisor /run/os rw,nosuid,nodev - tmpfs tmpfs rw,size=405464k,nr_inodes=819200,mode=755
813 750 0:24 /udev /run/udev ro,nosuid,nodev - tmpfs tmpfs rw,size=405464k,nr_inodes=819200,mode=755
814 750 0:24 /machine-id /etc/machine-id ro - tmpfs tmpfs rw,size=405464k,nr_inodes=819200,mode=755
815 750 0:24 /docker.sock /run/docker.sock rw,nosuid,nodev - tmpfs tmpfs rw,size=405464k,nr_inodes=819200,mode=755
816 750 0:24 /dbus /run/dbus ro,nosuid,nodev - tmpfs tmpfs rw,size=405464k,nr_inodes=819200,mode=755
820 750 0:24 /containerd/containerd.sock /run/containerd/containerd.sock rw,nosuid,nodev - tmpfs tmpfs rw,size=405464k,nr_inodes=819200,mode=755
821 750 0:24 /systemd/journal/socket /run/systemd/journal/socket rw,nosuid,nodev - tmpfs tmpfs rw,size=405464k,nr_inodes=819200,mode=755
"""


@pytest.fixture(name="nvme_data_disk")
async def fixture_nvme_data_disk(
    udisks2_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
    coresys: CoreSys,
    dbus_session_bus: MessageBus,
) -> NVMeControllerService:
    """Mock using an NVMe data disk."""
    nvme_service = (
        await mock_dbus_services(
            {
                "udisks2_block": "/org/freedesktop/UDisks2/block_devices/nvme0n1",
                "udisks2_drive": "/org/freedesktop/UDisks2/drives/Samsung_SSD_970_EVO_Plus_2TB_S40123456789ABC",
                "udisks2_nvme_controller": "/org/freedesktop/UDisks2/drives/Samsung_SSD_970_EVO_Plus_2TB_S40123456789ABC",
            },
            dbus_session_bus,
        )
    )["udisks2_nvme_controller"]
    udisks2_manager: UDisks2ManagerService = udisks2_services["udisks2_manager"]
    udisks2_manager.block_devices.append(
        "/org/freedesktop/UDisks2/block_devices/nvme0n1"
    )
    await coresys.dbus.udisks2.update()

    with (
        patch(
            "supervisor.hardware.disk.Path.read_text",
            return_value=MOCK_MOUNTINFO,
        ),
        patch("supervisor.hardware.disk.Path.is_block_device", return_value=True),
        patch(
            "supervisor.hardware.disk.Path.resolve",
            return_value=Path(
                "/sys/devices/platform/soc/ffe07000.nvme/nvme_host/nvme0/nvme0:0000/block/nvme0n1/nvme0n1p8"
            ),
        ),
    ):
        yield nvme_service


def test_system_partition_disk(coresys: CoreSys):
    """Test if it is a system disk/partition."""
    disk = Device(
        "sda1",
        Path("/dev/sda1"),
        Path("/sys/bus/usb/001"),
        "block",
        None,
        [],
        {"MAJOR": "5", "MINOR": "10"},
        [],
    )

    assert not coresys.hardware.disk.is_used_by_system(disk)

    disk = Device(
        "sda1",
        Path("/dev/sda1"),
        Path("/sys/bus/usb/001"),
        "block",
        None,
        [],
        {"MAJOR": "5", "MINOR": "10", "ID_FS_LABEL": "hassos-overlay"},
        [],
    )

    assert coresys.hardware.disk.is_used_by_system(disk)

    coresys.hardware.update_device(disk)
    disk_root = Device(
        "sda",
        Path("/dev/sda"),
        Path("/sys/bus/usb/001"),
        "block",
        None,
        [],
        {"MAJOR": "5", "MINOR": "0"},
        [Path("/dev/sda1")],
    )

    assert coresys.hardware.disk.is_used_by_system(disk_root)


def test_free_space(coresys):
    """Test free space helper."""
    with patch("shutil.disk_usage", return_value=(42, 42, 2 * (1024.0**3))):
        free = coresys.hardware.disk.get_disk_free_space("/data")

    assert free == 2.0


def test_total_space(coresys):
    """Test total space helper."""
    with patch("shutil.disk_usage", return_value=(10 * (1024.0**3), 42, 42)):
        total = coresys.hardware.disk.get_disk_total_space("/data")

    assert total == 10.0


def test_used_space(coresys):
    """Test used space helper."""
    with patch("shutil.disk_usage", return_value=(42, 8 * (1024.0**3), 42)):
        used = coresys.hardware.disk.get_disk_used_space("/data")

    assert used == 8.0


def test_get_mountinfo(coresys):
    """Test mountinfo helper."""
    mountinfo = coresys.hardware.disk._get_mountinfo("/proc")
    assert mountinfo[4] == "/proc"


def test_get_mount_source(coresys):
    """Test mount source helper."""
    # For /proc the mount source is known to be "proc"...
    mount_source = coresys.hardware.disk._get_mount_source("/proc")
    assert mount_source == "proc"


def test_try_get_emmc_life_time(coresys, tmp_path):
    """Test eMMC life time helper."""
    fake_life_time = tmp_path / "fake-mmcblk0-lifetime"
    fake_life_time.write_text("0x01 0x02\n")

    with patch(
        "supervisor.hardware.disk._BLOCK_DEVICE_EMMC_LIFE_TIME",
        str(tmp_path / "fake-{}-lifetime"),
    ):
        value = coresys.hardware.disk._try_get_emmc_life_time("mmcblk0")
    assert value == 10.0


async def test_try_get_nvme_life_time(
    coresys: CoreSys, nvme_data_disk: NVMeControllerService
):
    """Test getting lifetime info from an NVMe."""
    lifetime = await coresys.hardware.disk.get_disk_life_time(
        coresys.config.path_supervisor
    )
    assert lifetime == 1

    nvme_data_disk.smart_get_attributes_response["percent_used"].value = 50
    lifetime = await coresys.hardware.disk.get_disk_life_time(
        coresys.config.path_supervisor
    )
    assert lifetime == 50
