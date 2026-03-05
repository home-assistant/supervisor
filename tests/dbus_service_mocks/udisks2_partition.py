"""Mock of UDisks2 Partition service."""

from ctypes import c_uint32, c_uint64
from dataclasses import dataclass

from dbus_fast.service import PropertyAccess, dbus_property

from .base import DBusServiceMock, dbus_method

BUS_NAME = "org.freedesktop.UDisks2"
DEFAULT_OBJECT_PATH = "/org/freedesktop/UDisks2/block_devices/sda1"


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return Partition(object_path if object_path else DEFAULT_OBJECT_PATH)


@dataclass(slots=True)
class PartitionFixture:
    """Partition fixture."""

    Number: c_uint32
    Type: str
    Flags: c_uint64
    Offset: c_uint64
    Size: c_uint64
    Name: str
    UUID: str
    Table: str
    IsContainer: bool
    IsContained: bool


FIXTURES: dict[str, PartitionFixture] = {
    "/org/freedesktop/UDisks2/block_devices/mmcblk1p1": PartitionFixture(
        Number=1,
        Type="0x0c",
        Flags=128,
        Offset=8388608,
        Size=25165824,
        Name="",
        UUID="48617373-01",
        Table="/org/freedesktop/UDisks2/block_devices/mmcblk1",
        IsContainer=False,
        IsContained=False,
    ),
    "/org/freedesktop/UDisks2/block_devices/mmcblk1p2": PartitionFixture(
        Number=2,
        Type="0x05",
        Flags=0,
        Offset=33554432,
        Size=600834048,
        Name="",
        UUID="48617373-02",
        Table="/org/freedesktop/UDisks2/block_devices/mmcblk1",
        IsContainer=True,
        IsContained=False,
    ),
    "/org/freedesktop/UDisks2/block_devices/mmcblk1p3": PartitionFixture(
        Number=3,
        Type="0x83",
        Flags=0,
        Offset=635437056,
        Size=100663296,
        Name="",
        UUID="48617373-03",
        Table="/org/freedesktop/UDisks2/block_devices/mmcblk1",
        IsContainer=False,
        IsContained=False,
    ),
    "/org/freedesktop/UDisks2/block_devices/sda1": PartitionFixture(
        Number=1,
        Type="0fc63daf-8483-4772-8e79-3d69d8477de4",
        Flags=0,
        Offset=1048576,
        Size=250058113024,
        Name="hassos-data-external",
        UUID="6f3f99f4-4d34-476b-b051-77886da57fa9",
        Table="/org/freedesktop/UDisks2/block_devices/sda",
        IsContainer=False,
        IsContained=False,
    ),
    "/org/freedesktop/UDisks2/block_devices/sdb1": PartitionFixture(
        Number=1,
        Type="0x0c",
        Flags=128,
        Offset=1048576,
        Size=67108864,
        Name="",
        UUID="",
        Table="/org/freedesktop/UDisks2/block_devices/sdb",
        IsContainer=False,
        IsContained=False,
    ),
}


class Partition(DBusServiceMock):
    """Block mock.

    gdbus introspect --system --dest org.freedesktop.UDisks2 --object-path /org/freedesktop/UDisks2/block_devices/sda1
    """

    interface = "org.freedesktop.UDisks2.Partition"

    def __init__(self, object_path: str):
        """Initialize object."""
        super().__init__()
        self.object_path = object_path
        self.fixture: PartitionFixture = FIXTURES[object_path]

    @dbus_property(access=PropertyAccess.READ)
    def Number(self) -> "u":
        """Get Number."""
        return self.fixture.Number

    @dbus_property(access=PropertyAccess.READ)
    def Type(self) -> "s":
        """Get Type."""
        return self.fixture.Type

    @dbus_property(access=PropertyAccess.READ)
    def Flags(self) -> "t":
        """Get Flags."""
        return self.fixture.Flags

    @dbus_property(access=PropertyAccess.READ)
    def Offset(self) -> "t":
        """Get Offset."""
        return self.fixture.Offset

    @dbus_property(access=PropertyAccess.READ)
    def Size(self) -> "t":
        """Get Size."""
        return self.fixture.Size

    @dbus_property(access=PropertyAccess.READ)
    def Name(self) -> "s":
        """Get Name."""
        return self.fixture.Name

    @dbus_property(access=PropertyAccess.READ)
    def UUID(self) -> "s":
        """Get UUID."""
        return self.fixture.UUID

    @dbus_property(access=PropertyAccess.READ)
    def Table(self) -> "o":
        """Get Table."""
        return self.fixture.Table

    @dbus_property(access=PropertyAccess.READ)
    def IsContainer(self) -> "b":
        """Get IsContainer."""
        return self.fixture.IsContainer

    @dbus_property(access=PropertyAccess.READ)
    def IsContained(self) -> "b":
        """Get IsContained."""
        return self.fixture.IsContained

    @dbus_method()
    def SetType(self, type_: "s", options: "a{sv}") -> None:
        """Do SetType method."""

    @dbus_method()
    def SetName(self, name: "s", options: "a{sv}") -> None:
        """Do SetName method."""

    @dbus_method()
    def SetFlags(self, flags: "t", options: "a{sv}") -> None:
        """Do SetFlags method."""

    @dbus_method()
    def Resize(self, size: "t", options: "a{sv}") -> None:
        """Do Resize method."""

    @dbus_method()
    def Delete(self, options: "a{sv}") -> None:
        """Do Delete method."""
