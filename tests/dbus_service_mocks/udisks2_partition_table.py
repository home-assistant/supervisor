"""Mock of UDisks2 Partition Table service."""

from dataclasses import dataclass

from dbus_fast.service import PropertyAccess, dbus_property

from .base import DBusServiceMock, dbus_method

BUS_NAME = "org.freedesktop.UDisks2"
DEFAULT_OBJECT_PATH = "/org/freedesktop/UDisks2/block_devices/sda"


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return PartitionTable(object_path if object_path else DEFAULT_OBJECT_PATH)


@dataclass(slots=True)
class PartitionTableFixture:
    """PartitionTable fixture."""

    Partitions: list[str]
    Type: str


FIXTURES: dict[str, PartitionTableFixture] = {
    "/org/freedesktop/UDisks2/block_devices/mmcblk1": PartitionTableFixture(
        Partitions=[
            "/org/freedesktop/UDisks2/block_devices/mmcblk1p1",
            "/org/freedesktop/UDisks2/block_devices/mmcblk1p2",
            "/org/freedesktop/UDisks2/block_devices/mmcblk1p3",
        ],
        Type="dos",
    ),
    "/org/freedesktop/UDisks2/block_devices/sda": PartitionTableFixture(
        Partitions=["/org/freedesktop/UDisks2/block_devices/sda1"], Type="gpt"
    ),
    "/org/freedesktop/UDisks2/block_devices/sdb": PartitionTableFixture(
        Partitions=["/org/freedesktop/UDisks2/block_devices/sdb1"], Type="gpt"
    ),
    "/org/freedesktop/UDisks2/block_devices/multi_part_table1": PartitionTableFixture(
        Partitions=[], Type="gpt"
    ),
    "/org/freedesktop/UDisks2/block_devices/multi_part_table2": PartitionTableFixture(
        Partitions=[], Type="gpt"
    ),
}


class PartitionTable(DBusServiceMock):
    """PartitionTable mock.

    gdbus introspect --system --dest org.freedesktop.UDisks2 --object-path /org/freedesktop/UDisks2/block_devices/sda
    """

    interface = "org.freedesktop.UDisks2.PartitionTable"
    new_partition = "/org/freedesktop/UDisks2/block_devices/sda1"

    def __init__(self, object_path: str):
        """Initialize object."""
        super().__init__()
        self.object_path = object_path
        self.fixture: PartitionTableFixture = FIXTURES[object_path]

    @dbus_property(access=PropertyAccess.READ)
    def Partitions(self) -> "ao":
        """Get Partitions."""
        return self.fixture.Partitions

    @dbus_property(access=PropertyAccess.READ)
    def Type(self) -> "s":
        """Get Type."""
        return self.fixture.Type

    @dbus_method()
    def CreatePartition(
        self, offset: "t", size: "t", type_: "s", name: "s", options: "a{sv}"
    ) -> "o":
        """Do CreatePartition method."""
        return self.new_partition

    @dbus_method()
    def CreatePartitionAndFormat(
        self,
        offset: "t",
        size: "t",
        type_: "s",
        name: "s",
        options: "a{sv}",
        format_type_: "s",
        format_options: "a{sv}",
    ) -> "o":
        """Do CreatePartitionAndFormat method."""
        return self.new_partition
