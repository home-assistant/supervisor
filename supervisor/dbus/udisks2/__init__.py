"""Interface to UDisks2 over D-Bus."""

import asyncio
import logging
from typing import Any

from awesomeversion import AwesomeVersion
from dbus_fast.aio import MessageBus

from ...exceptions import (
    DBusError,
    DBusInterfaceError,
    DBusObjectError,
    DBusServiceUnkownError,
)
from ..const import (
    DBUS_ATTR_SUPPORTED_FILESYSTEMS,
    DBUS_ATTR_VERSION,
    DBUS_IFACE_BLOCK,
    DBUS_IFACE_DRIVE,
    DBUS_IFACE_UDISKS2_MANAGER,
    DBUS_NAME_UDISKS2,
    DBUS_OBJECT_BASE,
    DBUS_OBJECT_UDISKS2,
    DBUS_OBJECT_UDISKS2_MANAGER,
)
from ..interface import DBusInterface, DBusInterfaceProxy, dbus_property
from ..utils import dbus_connected
from .block import UDisks2Block
from .const import UDISKS2_DEFAULT_OPTIONS
from .data import DeviceSpecification
from .drive import UDisks2Drive

_LOGGER: logging.Logger = logging.getLogger(__name__)


class UDisks2(DBusInterface):
    """Handle D-Bus interface for UDisks2 root object."""

    name: str = DBUS_NAME_UDISKS2
    bus_name: str = DBUS_NAME_UDISKS2
    object_path: str = DBUS_OBJECT_UDISKS2


class UDisks2Manager(DBusInterfaceProxy):
    """Handle D-Bus interface for UDisks2.

    http://storaged.org/doc/udisks2-api/latest/
    """

    name: str = DBUS_NAME_UDISKS2
    bus_name: str = DBUS_NAME_UDISKS2
    object_path: str = DBUS_OBJECT_UDISKS2_MANAGER
    properties_interface: str = DBUS_IFACE_UDISKS2_MANAGER

    _block_devices: dict[str, UDisks2Block] = {}
    _drives: dict[str, UDisks2Drive] = {}

    def __init__(self):
        """Initialize object."""
        super().__init__()
        self.udisks2_object_manager = UDisks2()

    async def connect(self, bus: MessageBus):
        """Connect to D-Bus."""
        try:
            await super().connect(bus)
            await self.udisks2_object_manager.connect(bus)
        except DBusError as err:
            _LOGGER.critical("Can't connect to udisks2: %s", err)
        except (DBusServiceUnkownError, DBusInterfaceError):
            _LOGGER.warning(
                "No udisks2 support on the host. Host control has been disabled."
            )
        else:
            # Register for signals on devices added/removed
            self.udisks2_object_manager.dbus.object_manager.on(
                "interfaces_added", self._interfaces_added
            )
            self.udisks2_object_manager.dbus.object_manager.on(
                "interfaces_removed", self._interfaces_removed
            )

    @dbus_connected
    async def update(self, changed: dict[str, Any] | None = None) -> None:
        """Update properties via D-Bus.

        Also rebuilds cache of available block devices and drives.
        """
        await super().update(changed)

        if not changed:
            # Cache block devices
            block_devices = await self.connected_dbus.Manager.call(
                "get_block_devices", UDISKS2_DEFAULT_OPTIONS
            )

            unchanged_blocks = self._block_devices.keys() & set(block_devices)
            for removed in self._block_devices.keys() - set(block_devices):
                self._block_devices[removed].shutdown()

            self._block_devices = {
                device: self._block_devices[device]
                if device in unchanged_blocks
                else await UDisks2Block.new(device, self.connected_dbus.bus)
                for device in block_devices
            }

            # For existing block devices, need to check their type and call update
            await asyncio.gather(
                *[self._block_devices[path].check_type() for path in unchanged_blocks]
            )
            await asyncio.gather(
                *[self._block_devices[path].update() for path in unchanged_blocks]
            )

            # Cache drives
            drives = {
                device.drive
                for device in self.block_devices
                if device.drive != DBUS_OBJECT_BASE
            }

            unchanged_drives = self._drives.keys() & set(drives)
            for removed in self._drives.keys() - drives:
                self._drives[removed].shutdown()

            self._drives = {
                drive: self._drives[drive]
                if drive in self._drives
                else await UDisks2Drive.new(drive, self.connected_dbus.bus)
                for drive in drives
            }

            # Update existing drives
            await asyncio.gather(
                *[self._drives[path].update() for path in unchanged_drives]
            )

    @property
    @dbus_property
    def version(self) -> AwesomeVersion:
        """UDisks2 version."""
        return AwesomeVersion(self.properties[DBUS_ATTR_VERSION])

    @property
    @dbus_property
    def supported_filesystems(self) -> list[str]:
        """Return list of supported filesystems."""
        return self.properties[DBUS_ATTR_SUPPORTED_FILESYSTEMS]

    @property
    def block_devices(self) -> list[UDisks2Block]:
        """List of available block devices."""
        return list(self._block_devices.values())

    @property
    def drives(self) -> list[UDisks2Drive]:
        """List of available drives."""
        return list(self._drives.values())

    @dbus_connected
    def get_drive(self, drive_path: str) -> UDisks2Drive:
        """Get additional info on drive from object path."""
        if drive_path not in self._drives:
            raise DBusObjectError(f"Drive {drive_path} not found")

        return self._drives[drive_path]

    @dbus_connected
    def get_block_device(self, device_path: str) -> UDisks2Block:
        """Get additional info on block device from object path."""
        if device_path not in self._block_devices:
            raise DBusObjectError(f"Block device {device_path} not found")

        return self._block_devices[device_path]

    @dbus_connected
    async def resolve_device(self, devspec: DeviceSpecification) -> list[UDisks2Block]:
        """Return list of device object paths for specification."""
        return await asyncio.gather(
            *[
                UDisks2Block.new(path, self.connected_dbus.bus, sync_properties=False)
                for path in await self.connected_dbus.Manager.call(
                    "resolve_device", devspec.to_dict(), UDISKS2_DEFAULT_OPTIONS
                )
            ]
        )

    @dbus_connected
    async def _interfaces_added(
        self, object_path: str, properties: dict[str, dict[str, Any]]
    ) -> None:
        """Interfaces added to a UDisks2 object."""
        if object_path in self._block_devices:
            await self._block_devices[object_path].update()
            return
        if object_path in self._drives:
            await self._drives[object_path].update()
            return

        if DBUS_IFACE_BLOCK in properties:
            self._block_devices[object_path] = await UDisks2Block.new(
                object_path, self.connected_dbus.bus
            )
            return

        if DBUS_IFACE_DRIVE in properties:
            self._drives[object_path] = await UDisks2Drive.new(
                object_path, self.connected_dbus.bus
            )

    async def _interfaces_removed(
        self, object_path: str, interfaces: list[str]
    ) -> None:
        """Interfaces removed from a UDisks2 object."""
        if object_path in self._block_devices and DBUS_IFACE_BLOCK in interfaces:
            self._block_devices[object_path].shutdown()
            del self._block_devices[object_path]
            return

        if object_path in self._drives and DBUS_IFACE_DRIVE in interfaces:
            self._drives[object_path].shutdown()
            del self._drives[object_path]

    def shutdown(self) -> None:
        """Shutdown the object and disconnect from D-Bus.

        This method is irreversible.
        """
        self.udisks2_object_manager.shutdown()
        for block_device in self.block_devices:
            block_device.shutdown()
        for drive in self.drives:
            drive.shutdown()
        super().shutdown()
