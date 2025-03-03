"""Test OS API."""

import asyncio
from dataclasses import replace
from pathlib import PosixPath
from unittest.mock import patch

from dbus_fast import DBusError, ErrorType, Variant
import pytest

from supervisor.const import CoreState
from supervisor.core import Core
from supervisor.coresys import CoreSys
from supervisor.exceptions import HassOSDataDiskError, HassOSError
from supervisor.os.data_disk import Disk
from supervisor.resolution.const import ContextType, IssueType
from supervisor.resolution.data import Issue

from tests.common import mock_dbus_services
from tests.dbus_service_mocks.agent_datadisk import DataDisk as DataDiskService
from tests.dbus_service_mocks.agent_system import System as SystemService
from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.logind import Logind as LogindService
from tests.dbus_service_mocks.udisks2 import UDisks2 as UDisks2Service
from tests.dbus_service_mocks.udisks2_block import Block as BlockService
from tests.dbus_service_mocks.udisks2_filesystem import Filesystem as FilesystemService
from tests.dbus_service_mocks.udisks2_partition import Partition as PartitionService
from tests.dbus_service_mocks.udisks2_partition_table import (
    PartitionTable as PartitionTableService,
)


@pytest.fixture(autouse=True)
async def add_unusable_drive(
    coresys: CoreSys,
    udisks2_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
) -> None:
    """Add mock drive with multiple partition tables for negative tests."""
    await mock_dbus_services(
        {
            "udisks2_block": [
                "/org/freedesktop/UDisks2/block_devices/multi_part_table1",
                "/org/freedesktop/UDisks2/block_devices/multi_part_table2",
            ],
            "udisks2_drive": "/org/freedesktop/UDisks2/drives/Test_Multiple_Partition_Tables_123456789",
        },
        coresys.dbus.bus,
    )

    udisks2_services["udisks2_manager"].block_devices = udisks2_services[
        "udisks2_manager"
    ].block_devices + [
        "/org/freedesktop/UDisks2/block_devices/multi_part_table1",
        "/org/freedesktop/UDisks2/block_devices/multi_part_table2",
    ]
    await coresys.dbus.udisks2.update()


async def tests_datadisk_current(coresys: CoreSys):
    """Test current datadisk."""
    assert coresys.os.datadisk.disk_used == Disk(
        vendor="",
        model="BJTD4R",
        serial="0x97cde291",
        id="BJTD4R-0x97cde291",
        size=31268536320,
        device_path=PosixPath("/dev/mmcblk1"),
        object_path="/org/freedesktop/UDisks2/drives/BJTD4R_0x97cde291",
        device_object_path="/org/freedesktop/UDisks2/block_devices/mmcblk1",
    )


@pytest.mark.parametrize(
    "new_disk",
    ["/dev/sdaaaa", "/dev/mmcblk1", "Generic-Flash-Disk-61BCDDB6"],
    ids=["non-existent", "unavailable drive by path", "unavailable drive by id"],
)
async def test_datadisk_move_fail(coresys: CoreSys, new_disk: str, os_available):
    """Test datadisk move to non-existent or invalid devices."""
    with pytest.raises(
        HassOSDataDiskError, match=f"'{new_disk}' not a valid data disk target!"
    ):
        await coresys.os.datadisk.migrate_disk(new_disk)


async def test_datadisk_list(coresys: CoreSys):
    """Test docker info api."""
    assert {drive.object_path for drive in coresys.dbus.udisks2.drives} == {
        "/org/freedesktop/UDisks2/drives/BJTD4R_0x97cde291",
        "/org/freedesktop/UDisks2/drives/Generic_Flash_Disk_61BCDDB6",
        "/org/freedesktop/UDisks2/drives/SSK_SSK_Storage_DF56419883D56",
        "/org/freedesktop/UDisks2/drives/Test_Multiple_Partition_Tables_123456789",
    }

    assert coresys.os.datadisk.available_disks == [
        Disk(
            vendor="SSK",
            model="SSK Storage",
            serial="DF56419883D56",
            id="SSK-SSK-Storage-DF56419883D56",
            size=250059350016,
            device_path=PosixPath("/dev/sda"),
            object_path="/org/freedesktop/UDisks2/drives/SSK_SSK_Storage_DF56419883D56",
            device_object_path="/org/freedesktop/UDisks2/block_devices/sda",
        )
    ]


@pytest.mark.parametrize(
    "new_disk",
    ["SSK-SSK-Storage-DF56419883D56", "/dev/sda"],
    ids=["by drive id", "by device path"],
)
async def test_datadisk_migrate(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
    new_disk: str,
    os_available,
):
    """Test migrating data disk."""
    datadisk_service: DataDiskService = all_dbus_services["agent_datadisk"]
    datadisk_service.ChangeDevice.calls.clear()
    logind_service: LogindService = all_dbus_services["logind"]
    logind_service.Reboot.calls.clear()

    with patch.object(Core, "shutdown") as shutdown:
        await coresys.os.datadisk.migrate_disk(new_disk)
        shutdown.assert_called_once()

    assert datadisk_service.ChangeDevice.calls == [("/dev/sda",)]
    assert logind_service.Reboot.calls == [(False,)]


@pytest.mark.parametrize(
    "new_disk",
    ["SSK-SSK-Storage-DF56419883D56", "/dev/sda"],
    ids=["by drive id", "by device path"],
)
async def test_datadisk_migrate_mark_data_move(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
    new_disk: str,
    os_available,
):
    """Test migrating data disk with os agent 1.5.0 or later."""
    datadisk_service: DataDiskService = all_dbus_services["agent_datadisk"]
    datadisk_service.ChangeDevice.calls.clear()
    datadisk_service.MarkDataMove.calls.clear()
    block_service: BlockService = all_dbus_services["udisks2_block"][
        "/org/freedesktop/UDisks2/block_devices/sda"
    ]
    block_service.Format.calls.clear()
    partition_table_service: PartitionTableService = all_dbus_services[
        "udisks2_partition_table"
    ]["/org/freedesktop/UDisks2/block_devices/sda"]
    partition_table_service.CreatePartition.calls.clear()
    logind_service: LogindService = all_dbus_services["logind"]
    logind_service.Reboot.calls.clear()

    all_dbus_services["os_agent"].emit_properties_changed({"Version": "1.5.0"})
    await all_dbus_services["os_agent"].ping()

    with patch.object(Core, "shutdown") as shutdown:
        await coresys.os.datadisk.migrate_disk(new_disk)
        shutdown.assert_called_once()

    assert datadisk_service.ChangeDevice.calls == []
    assert datadisk_service.MarkDataMove.calls == [()]
    assert block_service.Format.calls == [
        ("gpt", {"auth.no_user_interaction": Variant("b", True)})
    ]
    assert partition_table_service.CreatePartition.calls == [
        (
            0,
            0,
            "0FC63DAF-8483-4772-8E79-3D69D8477DE4",
            "hassos-data-external",
            {"auth.no_user_interaction": Variant("b", True)},
        )
    ]
    assert logind_service.Reboot.calls == [(False,)]


async def test_datadisk_migrate_too_small(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
    os_available,
):
    """Test migration stops and exits if new partition is too small."""
    datadisk_service: DataDiskService = all_dbus_services["agent_datadisk"]
    datadisk_service.MarkDataMove.calls.clear()
    logind_service: LogindService = all_dbus_services["logind"]
    logind_service.Reboot.calls.clear()

    partition_table_service: PartitionTableService = all_dbus_services[
        "udisks2_partition_table"
    ]["/org/freedesktop/UDisks2/block_devices/sda"]
    partition_table_service.CreatePartition.calls.clear()
    partition_table_service.new_partition = (
        "/org/freedesktop/UDisks2/block_devices/mmcblk1p3"
    )

    all_dbus_services["os_agent"].emit_properties_changed({"Version": "1.5.0"})
    await all_dbus_services["os_agent"].ping()

    with pytest.raises(
        HassOSDataDiskError,
        match=r"Cannot use SSK-SSK-Storage-DF56419883D56 as data disk as it is smaller then the current one",
    ):
        await coresys.os.datadisk.migrate_disk("SSK-SSK-Storage-DF56419883D56")

    assert partition_table_service.CreatePartition.calls
    assert datadisk_service.MarkDataMove.calls == []
    assert logind_service.Reboot.calls == []


async def test_datadisk_migrate_multiple_external_data_disks(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
    os_available,
):
    """Test migration stops when another hassos-data-external partition detected."""
    datadisk_service: DataDiskService = all_dbus_services["agent_datadisk"]
    datadisk_service.ChangeDevice.calls.clear()
    datadisk_service.MarkDataMove.calls.clear()

    sdb1_filesystem_service: FilesystemService = all_dbus_services[
        "udisks2_filesystem"
    ]["/org/freedesktop/UDisks2/block_devices/sdb1"]
    sdb1_filesystem_service.fixture = replace(
        sdb1_filesystem_service.fixture, MountPoints=[]
    )

    with pytest.raises(
        HassOSDataDiskError,
        match=r"Partition\(s\) /dev/sda1 have name 'hassos-data-external' which prevents migration",
    ):
        await coresys.os.datadisk.migrate_disk("Generic-Flash-Disk-61BCDDB6")

    assert datadisk_service.ChangeDevice.calls == []
    assert datadisk_service.MarkDataMove.calls == []


async def test_datadisk_migrate_between_external_renames(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
    os_available,
):
    """Test migration from one external data disk to another renames the original."""
    sdb1_partition_service: PartitionService = all_dbus_services["udisks2_partition"][
        "/org/freedesktop/UDisks2/block_devices/sdb1"
    ]
    sdb1_partition_service.SetName.calls.clear()

    sdb1_filesystem_service: FilesystemService = all_dbus_services[
        "udisks2_filesystem"
    ]["/org/freedesktop/UDisks2/block_devices/sdb1"]
    sdb1_filesystem_service.fixture = replace(
        sdb1_filesystem_service.fixture, MountPoints=[]
    )
    sdb1_block_service: BlockService = all_dbus_services["udisks2_block"][
        "/org/freedesktop/UDisks2/block_devices/sdb1"
    ]
    sdb1_block_service.fixture = replace(sdb1_block_service.fixture, Size=250058113024)

    datadisk_service: DataDiskService = all_dbus_services["agent_datadisk"]
    datadisk_service.MarkDataMove.calls.clear()
    datadisk_service.emit_properties_changed({"CurrentDevice": "/dev/sda1"})
    await datadisk_service.ping()

    all_dbus_services["os_agent"].emit_properties_changed({"Version": "1.5.0"})
    await all_dbus_services["os_agent"].ping()

    await coresys.os.datadisk.migrate_disk("Generic-Flash-Disk-61BCDDB6")

    assert datadisk_service.MarkDataMove.calls == [()]
    assert sdb1_partition_service.SetName.calls == [
        ("hassos-data-external-old", {"auth.no_user_interaction": Variant("b", True)})
    ]


async def test_datadisk_wipe_errors(
    coresys: CoreSys,
    all_dbus_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
    os_available,
):
    """Test errors during datadisk wipe."""
    system_service: SystemService = all_dbus_services["agent_system"]
    system_service.ScheduleWipeDevice.calls.clear()
    logind_service: LogindService = all_dbus_services["logind"]
    logind_service.Reboot.calls.clear()

    system_service.response_schedule_wipe_device = False
    with pytest.raises(
        HassOSDataDiskError, match="Can't schedule wipe of data disk, check host logs"
    ):
        await coresys.os.datadisk.wipe_disk()

    assert system_service.ScheduleWipeDevice.calls == [()]
    assert not logind_service.Reboot.calls

    system_service.ScheduleWipeDevice.calls.clear()
    system_service.response_schedule_wipe_device = DBusError(ErrorType.FAILED, "fail")
    with pytest.raises(
        HassOSDataDiskError, match="Can't schedule wipe of data disk: fail"
    ):
        await coresys.os.datadisk.wipe_disk()

    assert system_service.ScheduleWipeDevice.calls == [()]
    assert not logind_service.Reboot.calls

    system_service.ScheduleWipeDevice.calls.clear()
    system_service.response_schedule_wipe_device = True
    logind_service.side_effect_reboot = DBusError(ErrorType.FAILED, "fail")
    with (
        patch.object(Core, "shutdown"),
        pytest.raises(HassOSError, match="Can't restart device"),
    ):
        await coresys.os.datadisk.wipe_disk()

    assert system_service.ScheduleWipeDevice.calls == [()]
    assert logind_service.Reboot.calls == [(False,)]


async def test_multiple_datadisk_add_remove_signals(
    coresys: CoreSys,
    udisks2_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
    os_available,
):
    """Test multiple data disk issue created/removed on signal."""
    udisks2_service: UDisks2Service = udisks2_services["udisks2"]
    sdb1_block: BlockService = udisks2_services["udisks2_block"][
        "/org/freedesktop/UDisks2/block_devices/sdb1"
    ]

    await coresys.os.datadisk.load()
    await coresys.core.set_state(CoreState.RUNNING)

    assert coresys.resolution.issues == []
    assert coresys.resolution.suggestions == []

    sdb1_block.fixture = replace(sdb1_block.fixture, IdLabel="hassos-data")
    udisks2_service.InterfacesAdded(
        "/org/freedesktop/UDisks2/block_devices/sdb1",
        {
            "org.freedesktop.UDisks2.Block": {
                "Device": Variant("ay", b"/dev/sdb1"),
                "PreferredDevice": Variant("ay", b"/dev/sdb1"),
                "DeviceNumber": Variant("t", 2065),
                "Id": Variant("s", ""),
                "IdUsage": Variant("s", ""),
                "IdType": Variant("s", ""),
                "IdVersion": Variant("s", ""),
                "IdLabel": Variant("s", "hassos-data"),
                "IdUUID": Variant("s", ""),
            }
        },
    )
    await udisks2_service.ping()
    await asyncio.sleep(0.2)

    assert (
        Issue(IssueType.MULTIPLE_DATA_DISKS, ContextType.SYSTEM, reference="/dev/sdb1")
        in coresys.resolution.issues
    )

    udisks2_service.InterfacesRemoved(
        "/org/freedesktop/UDisks2/block_devices/sdb1",
        ["org.freedesktop.UDisks2.Block", "org.freedesktop.UDisks2.Filesystem"],
    )
    await udisks2_service.ping()
    await asyncio.sleep(0.2)

    assert coresys.resolution.issues == []


async def test_disabled_datadisk_add_remove_signals(
    coresys: CoreSys,
    udisks2_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
    os_available,
):
    """Test disabled data disk issue created/removed on signal."""
    udisks2_service: UDisks2Service = udisks2_services["udisks2"]
    sdb1_block: BlockService = udisks2_services["udisks2_block"][
        "/org/freedesktop/UDisks2/block_devices/sdb1"
    ]

    await coresys.os.datadisk.load()
    await coresys.core.set_state(CoreState.RUNNING)

    assert coresys.resolution.issues == []
    assert coresys.resolution.suggestions == []

    sdb1_block.fixture = replace(sdb1_block.fixture, IdLabel="hassos-data-dis")
    udisks2_service.InterfacesAdded(
        "/org/freedesktop/UDisks2/block_devices/sdb1",
        {
            "org.freedesktop.UDisks2.Block": {
                "Device": Variant("ay", b"/dev/sdb1"),
                "PreferredDevice": Variant("ay", b"/dev/sdb1"),
                "DeviceNumber": Variant("t", 2065),
                "Id": Variant("s", ""),
                "IdUsage": Variant("s", ""),
                "IdType": Variant("s", ""),
                "IdVersion": Variant("s", ""),
                "IdLabel": Variant("s", "hassos-data-dis"),
                "IdUUID": Variant("s", ""),
            }
        },
    )
    await udisks2_service.ping()
    await asyncio.sleep(0.2)

    assert (
        Issue(IssueType.DISABLED_DATA_DISK, ContextType.SYSTEM, reference="/dev/sdb1")
        in coresys.resolution.issues
    )

    udisks2_service.InterfacesRemoved(
        "/org/freedesktop/UDisks2/block_devices/sdb1",
        ["org.freedesktop.UDisks2.Block", "org.freedesktop.UDisks2.Filesystem"],
    )
    await udisks2_service.ping()
    await asyncio.sleep(0.2)

    assert coresys.resolution.issues == []
