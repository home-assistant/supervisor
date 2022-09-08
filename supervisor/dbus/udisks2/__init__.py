"""Interface to UDisks2 over D-Bus."""
import logging
from typing import Any

from supervisor.dbus.udisks2.block import UDisks2Block
from supervisor.dbus.udisks2.filesystem import UDisks2Filesystem

from ...exceptions import DBusError, DBusInterfaceError
from ...utils.dbus import DBus
from ..const import (
    DBUS_ATTR_SUPPORTED_FILESYSTEMS,
    DBUS_IFACE_UDISKS2_MANAGER,
    DBUS_NAME_UDISKS2,
    DBUS_OBJECT_UDISKS2,
)
from ..interface import DBusInterface, dbus_property
from ..utils import dbus_connected

_LOGGER: logging.Logger = logging.getLogger(__name__)


class UDisks2(DBusInterface):
    """UDisks2 function handler."""

    name = DBUS_NAME_UDISKS2

    def __init__(self) -> None:
        """Initialize Properties."""
        self.properties: dict[str, Any] = {}

    async def connect(self):
        """Connect to D-Bus."""
        try:
            self.dbus = await DBus.connect(DBUS_NAME_UDISKS2, DBUS_OBJECT_UDISKS2)
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
        return [
            UDisks2Block(block_device)
            for block_device in await self.dbus.Manager.GetBlockDevices()
        ]

    @dbus_connected
    async def get_filesystems(self) -> list[UDisks2Filesystem]:
        """Return list of all block devices."""
        filesystem_devices: list[UDisks2Filesystem] = []
        for block_device in await self.dbus.Manager.GetBlockDevices():
            filesystem_device = UDisks2Filesystem(block_device)
            try:
                assert filesystem_device.mountpoints
            except KeyError:
                continue
            filesystem_devices.append(filesystem_device)
        return filesystem_devices

    @dbus_connected
    async def update(self):
        """Update Properties."""
        self.properties = await self.dbus.get_properties(DBUS_IFACE_UDISKS2_MANAGER)
