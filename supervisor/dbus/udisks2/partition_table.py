"""Interface to UDisks2 Partition Table over D-Bus."""

from ..const import (
    DBUS_ATTR_PARTITIONS,
    DBUS_ATTR_TYPE,
    DBUS_IFACE_PARTITION_TABLE,
    DBUS_NAME_UDISKS2,
)
from ..interface import DBusInterfaceProxy, dbus_property
from ..utils import dbus_connected
from .const import UDISKS2_DEFAULT_OPTIONS, PartitionTableType
from .data import CreatePartitionOptions


class UDisks2PartitionTable(DBusInterfaceProxy):
    """Handle D-Bus interface for UDisks2 partition table device object.

    http://storaged.org/doc/udisks2-api/latest/gdbus-org.freedesktop.UDisks2.PartitionTable.html
    """

    name: str = DBUS_IFACE_PARTITION_TABLE
    bus_name: str = DBUS_NAME_UDISKS2
    properties_interface: str = DBUS_IFACE_PARTITION_TABLE

    def __init__(self, object_path: str, *, sync_properties: bool = True) -> None:
        """Initialize object."""
        self._object_path = object_path
        self.sync_properties = sync_properties
        super().__init__()

    @property
    def object_path(self) -> str:
        """Object path for dbus object."""
        return self._object_path

    @property
    @dbus_property
    def partitions(self) -> list[str]:
        """List of object paths of partitions that belong to this table.

        Provide to UDisks2.get_block_device for UDisks2Block object.
        """
        return self.properties[DBUS_ATTR_PARTITIONS]

    @property
    @dbus_property
    def type(self) -> PartitionTableType:
        """Type of partition table."""
        return PartitionTableType(self.properties[DBUS_ATTR_TYPE])

    @dbus_connected
    async def create_partition(
        self,
        offset: int = 0,
        size: int = 0,
        type_: str = "",
        name: str = "",
        options: CreatePartitionOptions | None = None,
    ) -> str:
        """Create a new partition and return object path of new block device.

        Type should be a GUID from https://en.wikipedia.org/wiki/GUID_Partition_Table#Partition_type_GUIDs
        for GPT type tables or a hexadecimal number for dos type tables. Can also use empty string
        and let UDisks2 choose a default based on partition table and OS.
        Provide return value with UDisks2Block.new. Or UDisks2.get_block_device after UDisks2.update.
        """
        partition_options = options.to_dict() if options else {}
        return await self.connected_dbus.PartitionTable.call(
            "create_partition",
            offset,
            size,
            type_,
            name,
            partition_options | UDISKS2_DEFAULT_OPTIONS,
        )
