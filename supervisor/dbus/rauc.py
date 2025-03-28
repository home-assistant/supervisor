"""D-Bus interface for rauc."""

from ctypes import c_uint32, c_uint64
import logging
from typing import Any, NotRequired, TypedDict

from dbus_fast.aio.message_bus import MessageBus

from ..exceptions import DBusError, DBusInterfaceError, DBusServiceUnkownError
from ..utils.dbus import DBusSignalWrapper
from .const import (
    DBUS_ATTR_BOOT_SLOT,
    DBUS_ATTR_COMPATIBLE,
    DBUS_ATTR_LAST_ERROR,
    DBUS_ATTR_OPERATION,
    DBUS_ATTR_VARIANT,
    DBUS_IFACE_RAUC_INSTALLER,
    DBUS_NAME_RAUC,
    DBUS_OBJECT_BASE,
    DBUS_SIGNAL_RAUC_INSTALLER_COMPLETED,
    RaucState,
)
from .interface import DBusInterfaceProxy
from .utils import dbus_connected

_LOGGER: logging.Logger = logging.getLogger(__name__)

SlotStatusDataType = TypedDict(
    "SlotStatusDataType",
    {
        "class": str,
        "type": str,
        "state": str,
        "device": str,
        "bundle.compatible": NotRequired[str],
        "sha256": NotRequired[str],
        "size": NotRequired[c_uint64],
        "installed.count": NotRequired[c_uint32],
        "bundle.version": NotRequired[str],
        "installed.timestamp": NotRequired[str],
        "status": NotRequired[str],
        "activated.count": NotRequired[c_uint32],
        "activated.timestamp": NotRequired[str],
        "boot-status": NotRequired[str],
        "bootname": NotRequired[str],
        "parent": NotRequired[str],
    },
)


class Rauc(DBusInterfaceProxy):
    """Handle D-Bus interface for rauc."""

    name: str = DBUS_NAME_RAUC
    bus_name: str = DBUS_NAME_RAUC
    object_path: str = DBUS_OBJECT_BASE
    properties_interface: str = DBUS_IFACE_RAUC_INSTALLER

    def __init__(self) -> None:
        """Initialize Properties."""
        super().__init__()

        self._operation: str | None = None
        self._last_error: str | None = None
        self._compatible: str | None = None
        self._variant: str | None = None
        self._boot_slot: str | None = None

    async def connect(self, bus: MessageBus):
        """Connect to D-Bus."""
        _LOGGER.info("Load dbus interface %s", self.name)
        try:
            await super().connect(bus)
        except DBusError:
            _LOGGER.warning("Can't connect to rauc")
        except (DBusServiceUnkownError, DBusInterfaceError):
            _LOGGER.warning("Host has no rauc support. OTA updates have been disabled.")

    @property
    def operation(self) -> str | None:
        """Return the current (global) operation."""
        return self._operation

    @property
    def last_error(self) -> str | None:
        """Return the last message of the last error that occurred."""
        return self._last_error

    @property
    def compatible(self) -> str | None:
        """Return the system compatible string."""
        return self._compatible

    @property
    def variant(self) -> str | None:
        """Return the system variant string."""
        return self._variant

    @property
    def boot_slot(self) -> str | None:
        """Return the used boot slot."""
        return self._boot_slot

    @dbus_connected
    async def install(self, raucb_file) -> None:
        """Install rauc bundle file."""
        await self.connected_dbus.Installer.call("install", str(raucb_file))

    @dbus_connected
    async def get_slot_status(self) -> list[tuple[str, SlotStatusDataType]]:
        """Get slot status."""
        return await self.connected_dbus.Installer.call("get_slot_status")

    @dbus_connected
    def signal_completed(self) -> DBusSignalWrapper:
        """Return a signal wrapper for completed signal."""
        return self.connected_dbus.signal(DBUS_SIGNAL_RAUC_INSTALLER_COMPLETED)

    @dbus_connected
    async def mark(self, state: RaucState, slot_identifier: str) -> tuple[str, str]:
        """Get slot status."""
        return await self.connected_dbus.Installer.call("mark", state, slot_identifier)

    @dbus_connected
    async def update(self, changed: dict[str, Any] | None = None) -> None:
        """Update Properties."""
        await super().update(changed)
        if not self.properties:
            _LOGGER.warning("Can't get properties for rauc")
            return

        self._operation = self.properties.get(DBUS_ATTR_OPERATION)
        self._last_error = self.properties.get(DBUS_ATTR_LAST_ERROR)
        self._compatible = self.properties.get(DBUS_ATTR_COMPATIBLE)
        self._variant = self.properties.get(DBUS_ATTR_VARIANT)
        self._boot_slot = self.properties.get(DBUS_ATTR_BOOT_SLOT)
