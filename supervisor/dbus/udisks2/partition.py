"""Interface to UDisks2 Partition over D-Bus."""

from ..const import (
    DBUS_ATTR_NAME,
    DBUS_ATTR_NUMBER,
    DBUS_ATTR_OFFSET,
    DBUS_ATTR_SIZE,
    DBUS_ATTR_TABLE,
    DBUS_ATTR_TYPE,
    DBUS_ATTR_UUID_UPPERCASE,
    DBUS_IFACE_PARTITION,
    DBUS_NAME_UDISKS2,
)
from ..interface import DBusInterfaceProxy, dbus_property
from ..utils import dbus_connected
from .const import UDISKS2_DEFAULT_OPTIONS
from .data import DeletePartitionOptions


class UDisks2Partition(DBusInterfaceProxy):
    """Handle D-Bus interface for UDisks2 Partition device object.

    http://storaged.org/doc/udisks2-api/latest/gdbus-org.freedesktop.UDisks2.Partition.html
    """

    name = DBUS_IFACE_PARTITION
    bus_name = DBUS_NAME_UDISKS2
    properties_interface = DBUS_IFACE_PARTITION

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
    def number(self) -> int:
        """Parition number in partition table."""
        return self.properties[DBUS_ATTR_NUMBER]

    @property
    @dbus_property
    def type(self) -> str:
        """Partition type."""
        return self.properties[DBUS_ATTR_TYPE]

    @property
    @dbus_property
    def offset(self) -> int:
        """Offset of partition in bytes."""
        return self.properties[DBUS_ATTR_OFFSET]

    @property
    @dbus_property
    def size(self) -> int:
        """Size of partition in bytes."""
        return self.properties[DBUS_ATTR_SIZE]

    @property
    @dbus_property
    def name_(self) -> str:
        """Name/label of partition if known."""
        return self.properties[DBUS_ATTR_NAME]

    @property
    @dbus_property
    def uuid(self) -> str:
        """UUID of partition if known."""
        return self.properties[DBUS_ATTR_UUID_UPPERCASE]

    @property
    @dbus_property
    def table(self) -> str:
        """Object path of the partition table this belongs to.

        Provide to UDisks2.get_block_device for UDisks2Block object.
        """
        return self.properties[DBUS_ATTR_TABLE]

    @dbus_connected
    async def set_type(self, type_: str) -> None:
        """Set the type of the partition.

        Type should be a GUID from https://en.wikipedia.org/wiki/GUID_Partition_Table#Partition_type_GUIDs
        for GPT type tables or a hexadecimal number for dos type tables. Can also use empty string
        and let UDisks2 choose a default based on partition table and OS.
        """
        await self.connected_dbus.Partition.call(
            "set_type", type_, UDISKS2_DEFAULT_OPTIONS
        )

    @dbus_connected
    async def set_name(self, name: str) -> None:
        """Set the name/label of the partition."""
        await self.connected_dbus.Partition.call(
            "set_name", name, UDISKS2_DEFAULT_OPTIONS
        )

    @dbus_connected
    async def resize(self, size: int = 0) -> None:
        """Attempt to increase size of partition by specified bytes. 0 means determine and use maximal size.

        Position/offset cannot be changed, only size. May be slightly bigger then requested.
        Raises error if allocation fails.
        """
        await self.connected_dbus.Partition.call(
            "resize", size, UDISKS2_DEFAULT_OPTIONS
        )

    @dbus_connected
    async def delete(self, options: DeletePartitionOptions | None = None) -> None:
        """Delete the partition."""
        delete_options = options.to_dict() if options else {}
        return await self.connected_dbus.Partition.call(
            "delete", delete_options | UDISKS2_DEFAULT_OPTIONS
        )
