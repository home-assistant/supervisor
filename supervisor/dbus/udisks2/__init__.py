"""Interface to UDisks2 over D-Bus."""
import logging

from dbus_next.aio.message_bus import MessageBus

from ...exceptions import DBusError, DBusInterfaceError
from ..const import (
    DBUS_ATTR_SUPPORTED_FILESYSTEMS,
    DBUS_IFACE_UDISKS2_MANAGER,
    DBUS_NAME_UDISKS2,
    DBUS_OBJECT_UDISKS2,
)
from ..interface import DBusInterfaceProxy, dbus_property
from ..utils import dbus_connected
from .block import UDisks2Block
from .filesystem import UDisks2Filesystem

_LOGGER: logging.Logger = logging.getLogger(__name__)


class UDisks2(DBusInterfaceProxy):
    """Handle D-Bus interface for UDisks2.

    http://storaged.org/doc/udisks2-api/latest/
    """

    name = DBUS_NAME_UDISKS2
    bus_name: str = DBUS_NAME_UDISKS2
    object_path: str = DBUS_OBJECT_UDISKS2
    properties_interface: str = DBUS_IFACE_UDISKS2_MANAGER

    async def connect(self, bus: MessageBus):
        """Connect to D-Bus."""
        try:
            await super().connect(bus)
        except DBusError:
            _LOGGER.warning("Can't connect to udisks2")
        except DBusInterfaceError:
            _LOGGER.warning(
                "No udisks2 support on the host. Host control has been disabled."
            )

    @property
    @dbus_property
    def supported_filesystems(self) -> list[str]:
        """Return list of supported filesystems."""
        return self.properties[DBUS_ATTR_SUPPORTED_FILESYSTEMS]

    @dbus_connected
    async def get_block_devices(self) -> list[UDisks2Block]:
        """Return list of all block devices."""
        devices: list[UDisks2Block] = []
        for block_device in await self.dbus.Manager.call_get_block_devices():
            device = UDisks2Block(block_device)
            await device.connect(self.dbus.bus)
            devices.append(device)
        return devices

    @dbus_connected
    async def get_filesystems(self) -> list[UDisks2Filesystem]:
        """Return list of all block devices containing a mountable filesystem."""
        filesystem_devices: list[UDisks2Filesystem] = []
        for block_device in await self.dbus.Manager.call_get_block_devices():
            filesystem_device = UDisks2Filesystem(block_device)
            await filesystem_device.connect(self.dbus.bus)
            # If we get a key error, this block device is not a filesystem device
            try:
                assert filesystem_device.mountpoints
            except KeyError:
                continue
            filesystem_devices.append(filesystem_device)
        return filesystem_devices
