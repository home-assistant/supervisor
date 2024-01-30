"""Mock of UDisks2 Block service."""

from ctypes import c_uint64
from dataclasses import dataclass

from dbus_fast import Variant
from dbus_fast.service import PropertyAccess, dbus_property

from .base import DBusServiceMock, dbus_method

BUS_NAME = "org.freedesktop.UDisks2"
DEFAULT_OBJECT_PATH = "/org/freedesktop/UDisks2/block_devices/sda"


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return Block(object_path if object_path else DEFAULT_OBJECT_PATH)


@dataclass(slots=True)
class BlockFixture:
    """Block fixture."""

    Device: bytes
    PreferredDevice: bytes
    Symlinks: list[bytes]
    DeviceNumber: c_uint64
    Id: str
    Size: c_uint64
    ReadOnly: bool
    Drive: str
    MDRaid: str
    MDRaidMember: str
    IdUsage: str
    IdType: str
    IdVersion: str
    IdLabel: str
    IdUUID: str
    Configuration: list[list[str | dict[str, Variant]]]
    CryptoBackingDevice: str
    HintPartitionable: bool
    HintSystem: bool
    HintIgnore: bool
    HintAuto: bool
    HintName: str
    HintIconName: str
    HintSymbolicIconName: str
    UserspaceMountOptions: list[str]


FIXTURES: dict[str, BlockFixture] = {
    "/org/freedesktop/UDisks2/block_devices/loop0": BlockFixture(
        Device=b"/dev/loop0",
        PreferredDevice=b"/dev/loop0",
        Symlinks=[],
        DeviceNumber=1792,
        Id="",
        Size=0,
        ReadOnly=False,
        Drive="/",
        MDRaid="/",
        MDRaidMember="/",
        IdUsage="",
        IdType="",
        IdVersion="",
        IdLabel="",
        IdUUID="",
        Configuration=[],
        CryptoBackingDevice="/",
        HintPartitionable=True,
        HintSystem=True,
        HintIgnore=False,
        HintAuto=False,
        HintName="",
        HintIconName="",
        HintSymbolicIconName="",
        UserspaceMountOptions=[],
    ),
    "/org/freedesktop/UDisks2/block_devices/mmcblk1": BlockFixture(
        Device=b"/dev/mmcblk1",
        PreferredDevice=b"/dev/mmcblk1",
        Symlinks=[
            b"/dev/disk/by-id/mmc-BJTD4R_0x97cde291",
            b"/dev/disk/by-path/platform-ffe07000.mmc",
        ],
        DeviceNumber=45824,
        Id="by-id-mmc-BJTD4R_0x97cde291",
        Size=31268536320,
        ReadOnly=False,
        Drive="/org/freedesktop/UDisks2/drives/BJTD4R_0x97cde291",
        MDRaid="/",
        MDRaidMember="/",
        IdUsage="",
        IdType="",
        IdVersion="",
        IdLabel="",
        IdUUID="",
        Configuration=[],
        CryptoBackingDevice="/",
        HintPartitionable=True,
        HintSystem=True,
        HintIgnore=False,
        HintAuto=False,
        HintName="",
        HintIconName="",
        HintSymbolicIconName="",
        UserspaceMountOptions=[],
    ),
    "/org/freedesktop/UDisks2/block_devices/mmcblk1p1": BlockFixture(
        Device=b"/dev/mmcblk1p1",
        PreferredDevice=b"/dev/mmcblk1p1",
        Symlinks=[
            b"/dev/disk/by-id/mmc-BJTD4R_0x97cde291-part1",
            b"/dev/disk/by-label/hassos-boot",
            b"/dev/disk/by-partlabel/hassos-boot",
            b"/dev/disk/by-partuuid/48617373-01",
            b"/dev/disk/by-path/platform-ffe07000.mmc-part1",
            b"/dev/disk/by-uuid/16DD-EED4",
        ],
        DeviceNumber=45825,
        Id="by-id-mmc-BJTD4R_0x97cde291-part1",
        Size=25165824,
        ReadOnly=False,
        Drive="/org/freedesktop/UDisks2/drives/BJTD4R_0x97cde291",
        MDRaid="/",
        MDRaidMember="/",
        IdUsage="filesystem",
        IdType="vfat",
        IdVersion="FAT16",
        IdLabel="hassos-boot",
        IdUUID="16DD-EED4",
        Configuration=[],
        CryptoBackingDevice="/",
        HintPartitionable=True,
        HintSystem=True,
        HintIgnore=False,
        HintAuto=False,
        HintName="",
        HintIconName="",
        HintSymbolicIconName="",
        UserspaceMountOptions=[],
    ),
    "/org/freedesktop/UDisks2/block_devices/mmcblk1p2": BlockFixture(
        Device=b"/dev/mmcblk1p2",
        PreferredDevice=b"/dev/mmcblk1p2",
        Symlinks=[
            b"/dev/disk/by-id/mmc-BJTD4R_0x97cde291-part2",
            b"/dev/disk/by-partuuid/48617373-02",
            b"/dev/disk/by-path/platform-ffe07000.mmc-part2",
        ],
        DeviceNumber=45826,
        Id="by-id-mmc-BJTD4R_0x97cde291-part2",
        Size=1024,
        ReadOnly=False,
        Drive="/org/freedesktop/UDisks2/drives/BJTD4R_0x97cde291",
        MDRaid="/",
        MDRaidMember="/",
        IdUsage="",
        IdType="",
        IdVersion="",
        IdLabel="",
        IdUUID="",
        Configuration=[],
        CryptoBackingDevice="/",
        HintPartitionable=True,
        HintSystem=True,
        HintIgnore=False,
        HintAuto=False,
        HintName="",
        HintIconName="",
        HintSymbolicIconName="",
        UserspaceMountOptions=[],
    ),
    "/org/freedesktop/UDisks2/block_devices/mmcblk1p3": BlockFixture(
        Device=b"/dev/mmcblk1p3",
        PreferredDevice=b"/dev/mmcblk1p3",
        Symlinks=[
            b"/dev/disk/by-id/mmc-BJTD4R_0x97cde291-part3",
            b"/dev/disk/by-label/hassos-overlay",
            b"/dev/disk/by-partuuid/48617373-03",
            b"/dev/disk/by-path/platform-ffe07000.mmc-part3",
            b"/dev/disk/by-uuid/0cd0d026-8c69-484e-bbf1-8197019fa7df",
        ],
        DeviceNumber=45827,
        Id="by-id-mmc-BJTD4R_0x97cde291-part3",
        Size=100663296,
        ReadOnly=False,
        Drive="/org/freedesktop/UDisks2/drives/BJTD4R_0x97cde291",
        MDRaid="/",
        MDRaidMember="/",
        IdUsage="filesystem",
        IdType="ext4",
        IdVersion="1.0",
        IdLabel="hassos-overlay",
        IdUUID="0cd0d026-8c69-484e-bbf1-8197019fa7df",
        Configuration=[],
        CryptoBackingDevice="/",
        HintPartitionable=True,
        HintSystem=True,
        HintIgnore=False,
        HintAuto=False,
        HintName="",
        HintIconName="",
        HintSymbolicIconName="",
        UserspaceMountOptions=[],
    ),
    "/org/freedesktop/UDisks2/block_devices/sda": BlockFixture(
        Device=b"/dev/sda\x00",
        PreferredDevice=b"/dev/sda\x00",
        Symlinks=[
            b"/dev/disk/by-id/usb-SSK_SSK_Storage_DF56419883D56-0:0\x00",
            b"/dev/disk/by-path/platform-xhci-hcd.1.auto-usb-0:1.4:1.0-scsi-0:0:0:0\x00",
        ],
        DeviceNumber=2048,
        Id="by-id-usb-SSK_SSK_Storage_DF56419883D56-0:0",
        Size=250059350016,
        ReadOnly=False,
        Drive="/org/freedesktop/UDisks2/drives/SSK_SSK_Storage_DF56419883D56",
        MDRaid="/",
        MDRaidMember="/",
        IdUsage="",
        IdType="",
        IdVersion="",
        IdLabel="",
        IdUUID="",
        Configuration=[],
        CryptoBackingDevice="/",
        HintPartitionable=True,
        HintSystem=False,
        HintIgnore=False,
        HintAuto=True,
        HintName="",
        HintIconName="",
        HintSymbolicIconName="",
        UserspaceMountOptions=[],
    ),
    "/org/freedesktop/UDisks2/block_devices/sda1": BlockFixture(
        Device=b"/dev/sda1\x00",
        PreferredDevice=b"/dev/sda1\x00",
        Symlinks=[
            b"/dev/disk/by-id/usb-SSK_SSK_Storage_DF56419883D56-0:0-part1\x00",
            b"/dev/disk/by-label/hassos-data-old\x00",
            b"/dev/disk/by-partlabel/hassos-data-external\x00",
            b"/dev/disk/by-partuuid/6f3f99f4-4d34-476b-b051-77886da57fa9\x00",
            b"/dev/disk/by-path/platform-xhci-hcd.1.auto-usb-0:1.4:1.0-scsi-0:0:0:0-part1\x00",
            b"/dev/disk/by-uuid/b82b23cb-0c47-4bbb-acf5-2a2afa8894a2\x00",
        ],
        DeviceNumber=2049,
        Id="by-id-usb-SSK_SSK_Storage_DF56419883D56-0:0-part1",
        Size=250058113024,
        ReadOnly=False,
        Drive="/org/freedesktop/UDisks2/drives/SSK_SSK_Storage_DF56419883D56",
        MDRaid="/",
        MDRaidMember="/",
        IdUsage="filesystem",
        IdType="ext4",
        IdVersion="1.0",
        IdLabel="hassos-data-old",
        IdUUID="b82b23cb-0c47-4bbb-acf5-2a2afa8894a2",
        Configuration=[],
        CryptoBackingDevice="/",
        HintPartitionable=True,
        HintSystem=False,
        HintIgnore=False,
        HintAuto=True,
        HintName="",
        HintIconName="",
        HintSymbolicIconName="",
        UserspaceMountOptions=[],
    ),
    "/org/freedesktop/UDisks2/block_devices/sdb": BlockFixture(
        Device=b"/dev/sdb\x00",
        PreferredDevice=b"/dev/sdb\x00",
        Symlinks=[
            b"/dev/disk/by-id/usb-Generic_Flash_Disk_61BCDDB6-0:0\x00",
            b"/dev/disk/by-path/platform-xhci-hcd.1.auto-usb-0:1.2:1.0-scsi-0:0:0:0\x00",
        ],
        DeviceNumber=2064,
        Id="",
        Size=8054112256,
        ReadOnly=False,
        Drive="/org/freedesktop/UDisks2/drives/Generic_Flash_Disk_61BCDDB6",
        MDRaid="/",
        MDRaidMember="/",
        IdUsage="",
        IdType="",
        IdVersion="",
        IdLabel="",
        IdUUID="",
        Configuration=[],
        CryptoBackingDevice="/",
        HintPartitionable=True,
        HintSystem=False,
        HintIgnore=False,
        HintAuto=True,
        HintName="",
        HintIconName="",
        HintSymbolicIconName="",
        UserspaceMountOptions=[],
    ),
    "/org/freedesktop/UDisks2/block_devices/sdb1": BlockFixture(
        Device=b"/dev/sdb1\x00",
        PreferredDevice=b"/dev/sdb1\x00",
        Symlinks=[
            b"/dev/disk/by-id/usb-Generic_Flash_Disk_61BCDDB6-0:0-part1\x00",
            b"/dev/disk/by-path/platform-xhci-hcd.1.auto-usb-0:1.2:1.0-scsi-0:0:0:0-part1\x00",
            b"/dev/disk/by-uuid/2802-1EDE\x00",
        ],
        DeviceNumber=2065,
        Id="by-uuid-2802-1EDE",
        Size=67108864,
        ReadOnly=False,
        Drive="/org/freedesktop/UDisks2/drives/Generic_Flash_Disk_61BCDDB6",
        MDRaid="/",
        MDRaidMember="/",
        IdUsage="filesystem",
        IdType="vfat",
        IdVersion="FAT16",
        IdLabel="",
        IdUUID="2802-1EDE",
        Configuration=[],
        CryptoBackingDevice="/",
        HintPartitionable=True,
        HintSystem=False,
        HintIgnore=False,
        HintAuto=True,
        HintName="",
        HintIconName="",
        HintSymbolicIconName="",
        UserspaceMountOptions=[],
    ),
    "/org/freedesktop/UDisks2/block_devices/zram1": BlockFixture(
        Device=b"/dev/zram1",
        PreferredDevice=b"/dev/zram1",
        Symlinks=[],
        DeviceNumber=64769,
        Id="",
        Size=33554432,
        ReadOnly=False,
        Drive="/",
        MDRaid="/",
        MDRaidMember="/",
        IdUsage="",
        IdType="",
        IdVersion="",
        IdLabel="",
        IdUUID="",
        Configuration=[],
        CryptoBackingDevice="/",
        HintPartitionable=True,
        HintSystem=True,
        HintIgnore=False,
        HintAuto=False,
        HintName="",
        HintIconName="",
        HintSymbolicIconName="",
        UserspaceMountOptions=[],
    ),
    "/org/freedesktop/UDisks2/block_devices/multi_part_table1": BlockFixture(
        Device=b"/dev/parttable1",
        PreferredDevice=b"/dev/parttable1",
        Symlinks=[],
        DeviceNumber=64769,
        Id="",
        Size=33554432,
        ReadOnly=False,
        Drive="/org/freedesktop/UDisks2/drives/Test_Multiple_Partition_Tables_123456789",
        MDRaid="/",
        MDRaidMember="/",
        IdUsage="",
        IdType="",
        IdVersion="",
        IdLabel="",
        IdUUID="",
        Configuration=[],
        CryptoBackingDevice="/",
        HintPartitionable=True,
        HintSystem=True,
        HintIgnore=False,
        HintAuto=False,
        HintName="",
        HintIconName="",
        HintSymbolicIconName="",
        UserspaceMountOptions=[],
    ),
    "/org/freedesktop/UDisks2/block_devices/multi_part_table2": BlockFixture(
        Device=b"/dev/parttable2",
        PreferredDevice=b"/dev/parttable2",
        Symlinks=[],
        DeviceNumber=64769,
        Id="",
        Size=33554432,
        ReadOnly=False,
        Drive="/org/freedesktop/UDisks2/drives/Test_Multiple_Partition_Tables_123456789",
        MDRaid="/",
        MDRaidMember="/",
        IdUsage="",
        IdType="",
        IdVersion="",
        IdLabel="",
        IdUUID="",
        Configuration=[],
        CryptoBackingDevice="/",
        HintPartitionable=True,
        HintSystem=True,
        HintIgnore=False,
        HintAuto=False,
        HintName="",
        HintIconName="",
        HintSymbolicIconName="",
        UserspaceMountOptions=[],
    ),
}


class Block(DBusServiceMock):
    """Block mock.

    gdbus introspect --system --dest org.freedesktop.UDisks2 --object-path /org/freedesktop/UDisks2/block_devices/sda
    """

    interface = "org.freedesktop.UDisks2.Block"

    def __init__(self, object_path: str):
        """Initialize object."""
        super().__init__()
        self.object_path = object_path
        self.fixture: BlockFixture = FIXTURES[object_path]

    @dbus_property(access=PropertyAccess.READ)
    def Device(self) -> "ay":
        """Get Device."""
        return self.fixture.Device

    @dbus_property(access=PropertyAccess.READ)
    def PreferredDevice(self) -> "ay":
        """Get PreferredDevice."""
        return self.fixture.PreferredDevice

    @dbus_property(access=PropertyAccess.READ)
    def Symlinks(self) -> "aay":
        """Get Symlinks."""
        return self.fixture.Symlinks

    @dbus_property(access=PropertyAccess.READ)
    def DeviceNumber(self) -> "t":
        """Get DeviceNumber."""
        return self.fixture.DeviceNumber

    @dbus_property(access=PropertyAccess.READ)
    def Id(self) -> "s":
        """Get Id."""
        return self.fixture.Id

    @dbus_property(access=PropertyAccess.READ)
    def Size(self) -> "t":
        """Get Size."""
        return self.fixture.Size

    @dbus_property(access=PropertyAccess.READ)
    def ReadOnly(self) -> "b":
        """Get ReadOnly."""
        return self.fixture.ReadOnly

    @dbus_property(access=PropertyAccess.READ)
    def Drive(self) -> "o":
        """Get Drive."""
        return self.fixture.Drive

    @dbus_property(access=PropertyAccess.READ)
    def MDRaid(self) -> "o":
        """Get MDRaid."""
        return self.fixture.MDRaid

    @dbus_property(access=PropertyAccess.READ)
    def MDRaidMember(self) -> "o":
        """Get MDRaidMember."""
        return self.fixture.MDRaidMember

    @dbus_property(access=PropertyAccess.READ)
    def IdUsage(self) -> "s":
        """Get IdUsage."""
        return self.fixture.IdUsage

    @dbus_property(access=PropertyAccess.READ)
    def IdType(self) -> "s":
        """Get IdType."""
        return self.fixture.IdType

    @dbus_property(access=PropertyAccess.READ)
    def IdVersion(self) -> "s":
        """Get IdVersion."""
        return self.fixture.IdVersion

    @dbus_property(access=PropertyAccess.READ)
    def IdLabel(self) -> "s":
        """Get IdLabel."""
        return self.fixture.IdLabel

    @dbus_property(access=PropertyAccess.READ)
    def IdUUID(self) -> "s":
        """Get IdUUID."""
        return self.fixture.IdUUID

    @dbus_property(access=PropertyAccess.READ)
    def Configuration(self) -> "a(sa{sv})":
        """Get Configuration."""
        return self.fixture.Configuration

    @dbus_property(access=PropertyAccess.READ)
    def CryptoBackingDevice(self) -> "o":
        """Get CryptoBackingDevice."""
        return self.fixture.CryptoBackingDevice

    @dbus_property(access=PropertyAccess.READ)
    def HintPartitionable(self) -> "b":
        """Get HintPartitionable."""
        return self.fixture.HintPartitionable

    @dbus_property(access=PropertyAccess.READ)
    def HintSystem(self) -> "b":
        """Get HintSystem."""
        return self.fixture.HintSystem

    @dbus_property(access=PropertyAccess.READ)
    def HintIgnore(self) -> "b":
        """Get HintIgnore."""
        return self.fixture.HintIgnore

    @dbus_property(access=PropertyAccess.READ)
    def HintAuto(self) -> "b":
        """Get HintAuto."""
        return self.fixture.HintAuto

    @dbus_property(access=PropertyAccess.READ)
    def HintName(self) -> "s":
        """Get HintName."""
        return self.fixture.HintName

    @dbus_property(access=PropertyAccess.READ)
    def HintIconName(self) -> "s":
        """Get HintIconName."""
        return self.fixture.HintIconName

    @dbus_property(access=PropertyAccess.READ)
    def HintSymbolicIconName(self) -> "s":
        """Get HintSymbolicIconName."""
        return self.fixture.HintSymbolicIconName

    @dbus_property(access=PropertyAccess.READ)
    def UserspaceMountOptions(self) -> "as":
        """Get UserspaceMountOptions."""
        return self.fixture.UserspaceMountOptions

    @dbus_method()
    def AddConfigurationItem(self, item: "(sa{sv})", options: "a{sv}") -> None:
        """Do AddConfigurationItem method."""

    @dbus_method()
    def RemoveConfigurationItem(self, item: "(sa{sv})", options: "a{sv}") -> None:
        """Do RemoveConfigurationItem method."""

    @dbus_method()
    def UpdateConfigurationItem(
        self, old_item: "(sa{sv})", new_item: "(sa{sv})", options: "a{sv}"
    ) -> None:
        """Do UpdateConfigurationItem method."""

    @dbus_method()
    def GetSecretConfiguration(self, options: "a{sv}") -> "a(sa{sv})":
        """Do GetSecretConfiguration method."""
        return []

    @dbus_method()
    def Format(self, type_: "s", options: "a{sv}") -> None:
        """Do Format method."""

    @dbus_method()
    def OpenForBackup(self, options: "a{sv}") -> "h":
        """Do OpenForBackup method."""
        return 100

    @dbus_method()
    def OpenForRestore(self, options: "a{sv}") -> "h":
        """Do OpenForRestore method."""
        return 101

    @dbus_method()
    def OpenForBenchmark(self, options: "a{sv}") -> "h":
        """Do OpenForBenchmark method."""
        return 102

    @dbus_method()
    def OpenDevice(self, mode: "s", options: "a{sv}") -> "h":
        """Do OpenDevice method."""
        return 103

    @dbus_method()
    def Rescan(self, options: "a{sv}") -> None:
        """Do Rescan method."""
