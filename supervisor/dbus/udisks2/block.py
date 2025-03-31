"""Interface to UDisks2 Block Device over D-Bus."""

import asyncio
from collections.abc import Callable
from pathlib import Path
from typing import Any

from awesomeversion import AwesomeVersion
from dbus_fast.aio import MessageBus

from ..const import (
    DBUS_ATTR_DEVICE,
    DBUS_ATTR_DEVICE_NUMBER,
    DBUS_ATTR_DRIVE,
    DBUS_ATTR_HINT_AUTO,
    DBUS_ATTR_HINT_IGNORE,
    DBUS_ATTR_HINT_NAME,
    DBUS_ATTR_HINT_SYSTEM,
    DBUS_ATTR_ID,
    DBUS_ATTR_ID_ID_TYPE,
    DBUS_ATTR_ID_LABEL,
    DBUS_ATTR_ID_USAGE,
    DBUS_ATTR_ID_UUID,
    DBUS_ATTR_ID_VERSION,
    DBUS_ATTR_READ_ONLY,
    DBUS_ATTR_SIZE,
    DBUS_ATTR_SYMLINKS,
    DBUS_IFACE_BLOCK,
    DBUS_IFACE_FILESYSTEM,
    DBUS_IFACE_PARTITION,
    DBUS_IFACE_PARTITION_TABLE,
    DBUS_NAME_UDISKS2,
)
from ..interface import DBusInterfaceProxy, dbus_property
from ..utils import dbus_connected
from .const import UDISKS2_DEFAULT_OPTIONS, FormatType
from .data import FormatOptions, udisks2_bytes_to_path
from .filesystem import UDisks2Filesystem
from .partition import UDisks2Partition
from .partition_table import UDisks2PartitionTable

ADDITIONAL_INTERFACES: dict[str, Callable[[str], DBusInterfaceProxy]] = {
    DBUS_IFACE_FILESYSTEM: UDisks2Filesystem
}


class UDisks2Block(DBusInterfaceProxy):
    """Handle D-Bus interface for UDisks2 block device object.

    http://storaged.org/doc/udisks2-api/latest/gdbus-org.freedesktop.UDisks2.Block.html
    """

    name: str = DBUS_IFACE_BLOCK
    bus_name: str = DBUS_NAME_UDISKS2
    properties_interface: str = DBUS_IFACE_BLOCK

    _filesystem: UDisks2Filesystem | None = None
    _partition: UDisks2Partition | None = None
    _partition_table: UDisks2PartitionTable | None = None

    def __init__(self, object_path: str, *, sync_properties: bool = True) -> None:
        """Initialize object."""
        self._object_path = object_path
        self.sync_properties = sync_properties
        super().__init__()

    async def connect(self, bus: MessageBus) -> None:
        """Connect to bus."""
        await super().connect(bus)
        await self._reload_interfaces()

    @staticmethod
    async def new(
        object_path: str, bus: MessageBus, *, sync_properties: bool = True
    ) -> "UDisks2Block":
        """Create and connect object."""
        obj = UDisks2Block(object_path, sync_properties=sync_properties)
        await obj.connect(bus)
        return obj

    @property
    def object_path(self) -> str:
        """Object path for dbus object."""
        return self._object_path

    @property
    def filesystem(self) -> UDisks2Filesystem | None:
        """Filesystem interface if block device is one."""
        return self._filesystem

    @property
    def partition(self) -> UDisks2Partition | None:
        """Partition interface if block device is one."""
        return self._partition

    @property
    def partition_table(self) -> UDisks2PartitionTable | None:
        """Partition table interface if block device is one."""
        return self._partition_table

    @property
    @dbus_property
    def device(self) -> Path:
        """Return device file."""
        return udisks2_bytes_to_path(self.properties[DBUS_ATTR_DEVICE])

    @property
    @dbus_property
    def id(self) -> str:
        """Return unique identifer."""
        return self.properties[DBUS_ATTR_ID]

    @property
    @dbus_property
    def size(self) -> int:
        """Return size."""
        return self.properties[DBUS_ATTR_SIZE]

    @property
    @dbus_property
    def read_only(self) -> bool:
        """Return whether device is read only."""
        return self.properties[DBUS_ATTR_READ_ONLY]

    @property
    @dbus_property
    def symlinks(self) -> list[Path]:
        """Return list of symlinks."""
        return [
            udisks2_bytes_to_path(symlink)
            for symlink in self.properties[DBUS_ATTR_SYMLINKS]
        ]

    @property
    @dbus_property
    def device_number(self) -> int:
        """Return device number."""
        return self.properties[DBUS_ATTR_DEVICE_NUMBER]

    @property
    @dbus_property
    def id_usage(self) -> str:
        """Return expected usage of structured data by probing signatures (if known)."""
        return self.properties[DBUS_ATTR_ID_USAGE]

    @property
    @dbus_property
    def id_type(self) -> str:
        """Return more specific usage information on structured data (if known)."""
        return self.properties[DBUS_ATTR_ID_ID_TYPE]

    @property
    @dbus_property
    def id_version(self) -> AwesomeVersion:
        """Return version of filesystem or other structured data."""
        return AwesomeVersion(self.properties[DBUS_ATTR_ID_VERSION])

    @property
    @dbus_property
    def id_label(self) -> str:
        """Return label of filesystem or other structured data."""
        return self.properties[DBUS_ATTR_ID_LABEL]

    @property
    @dbus_property
    def id_uuid(self) -> str:
        """Return uuid of filesystem or other structured data."""
        return self.properties[DBUS_ATTR_ID_UUID]

    @property
    @dbus_property
    def hint_auto(self) -> bool:
        """Return true if device should be automatically started (mounted, unlocked, etc)."""
        return self.properties[DBUS_ATTR_HINT_AUTO]

    @property
    @dbus_property
    def hint_ignore(self) -> bool:
        """Return true if device should be hidden from users."""
        return self.properties[DBUS_ATTR_HINT_IGNORE]

    @property
    @dbus_property
    def hint_name(self) -> str:
        """Return name that should be presented to users."""
        return self.properties[DBUS_ATTR_HINT_NAME]

    @property
    @dbus_property
    def hint_system(self) -> bool:
        """Return true if device is considered a system device.."""
        return self.properties[DBUS_ATTR_HINT_SYSTEM]

    @property
    @dbus_property
    def drive(self) -> str:
        """Return object path for drive.

        Provide to UDisks2.get_drive for UDisks2Drive object.
        """
        return self.properties[DBUS_ATTR_DRIVE]

    @dbus_connected
    async def update(self, changed: dict[str, Any] | None = None) -> None:
        """Update properties via D-Bus."""
        await super().update(changed)

        if not changed:
            await asyncio.gather(
                *[
                    intr.update()
                    for intr in (self.filesystem, self.partition, self.partition_table)
                    if intr
                ]
            )

    @dbus_connected
    async def check_type(self) -> None:
        """Check if type of block device has changed and adjust interfaces if so."""
        introspection = await self.connected_dbus.introspect()
        interfaces = {intr.name for intr in introspection.interfaces}

        # If interfaces changed, update the proxy from introspection and reload interfaces
        if interfaces != set(self.connected_dbus.proxies.keys()):
            await self.connected_dbus.init_proxy(introspection=introspection)
            await self._reload_interfaces()

    @dbus_connected
    async def _reload_interfaces(self) -> None:
        """Reload interfaces from introspection as necessary."""
        # Check if block device is a filesystem
        if not self.filesystem and DBUS_IFACE_FILESYSTEM in self.connected_dbus.proxies:
            self._filesystem = UDisks2Filesystem(
                self.object_path, sync_properties=self.sync_properties
            )
            await self._filesystem.initialize(self.connected_dbus)

        elif (
            self.filesystem and DBUS_IFACE_FILESYSTEM not in self.connected_dbus.proxies
        ):
            self.filesystem.stop_sync_property_changes()
            self._filesystem = None

        # Check if block device is a partition
        if not self.partition and DBUS_IFACE_PARTITION in self.connected_dbus.proxies:
            self._partition = UDisks2Partition(
                self.object_path, sync_properties=self.sync_properties
            )
            await self._partition.initialize(self.connected_dbus)

        elif self.partition and DBUS_IFACE_PARTITION not in self.connected_dbus.proxies:
            self.partition.stop_sync_property_changes()
            self._partition = None

        # Check if block device is a partition table
        if (
            not self.partition_table
            and DBUS_IFACE_PARTITION_TABLE in self.connected_dbus.proxies
        ):
            self._partition_table = UDisks2PartitionTable(
                self.object_path, sync_properties=self.sync_properties
            )
            await self._partition_table.initialize(self.connected_dbus)

        elif (
            self.partition_table
            and DBUS_IFACE_PARTITION_TABLE not in self.connected_dbus.proxies
        ):
            self.partition_table.stop_sync_property_changes()
            self._partition_table = None

    @dbus_connected
    async def format(
        self, type_: FormatType = FormatType.GPT, options: FormatOptions | None = None
    ) -> None:
        """Format block device."""
        format_options = options.to_dict() if options else {}
        await self.connected_dbus.Block.call(
            "format", type_, format_options | UDISKS2_DEFAULT_OPTIONS
        )
