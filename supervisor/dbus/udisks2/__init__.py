"""Interface to UDisks2 over D-Bus."""
from dataclasses import dataclass
import logging
from typing import Dict, TypedDict

from dbus_next.aio.message_bus import MessageBus
from dbus_next.signature import Variant
from typing_extensions import NotRequired

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

UDisks2StandardOptionsDataType = TypedDict(
    "UDisks2StandardOptionsDataType",
    {"auth.no_user_interaction": NotRequired[bool]},
)


@dataclass
class UDisks2StandardOptions:
    """UDisks2 standard options."""

    auth_no_user_interaction: bool | None

    @staticmethod
    def from_dict(data: UDisks2StandardOptionsDataType) -> "UDisks2StandardOptions":
        """Create UDisks2StandardOptions from dict."""
        return UDisks2StandardOptions(
            auth_no_user_interaction=data.get("auth.no_user_interaction"),
        )

    def to_dict(self) -> Dict[str, Variant]:
        """Return dict representation."""
        data = {"auth.no_user_interaction": Variant("b", self.auth_no_user_interaction)}
        return {k: v for k, v in data.items() if v.value is not None}


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
            # If there are no mountpoints, this block device is not a filesystem device
            if filesystem_device.mountpoints is None:
                continue
            filesystem_devices.append(filesystem_device)
        return filesystem_devices
