"""Interface to UDisks2 Drive over D-Bus."""

from datetime import UTC, datetime
from typing import Any

from dbus_fast.aio import MessageBus

from ..const import (
    DBUS_ATTR_CONNECTION_BUS,
    DBUS_ATTR_EJECTABLE,
    DBUS_ATTR_ID,
    DBUS_ATTR_MODEL,
    DBUS_ATTR_REMOVABLE,
    DBUS_ATTR_REVISION,
    DBUS_ATTR_SEAT,
    DBUS_ATTR_SERIAL,
    DBUS_ATTR_SIZE,
    DBUS_ATTR_TIME_DETECTED,
    DBUS_ATTR_VENDOR,
    DBUS_ATTR_WWN,
    DBUS_IFACE_DRIVE,
    DBUS_IFACE_NVME_CONTROLLER,
    DBUS_NAME_UDISKS2,
)
from ..interface import DBusInterfaceProxy, dbus_property
from ..utils import dbus_connected
from .const import UDISKS2_DEFAULT_OPTIONS
from .nvme_controller import UDisks2NVMeController


class UDisks2Drive(DBusInterfaceProxy):
    """Handle D-Bus interface for UDisks2 drive object.

    http://storaged.org/doc/udisks2-api/latest/gdbus-org.freedesktop.UDisks2.Drive.html
    """

    name: str = DBUS_IFACE_DRIVE
    bus_name: str = DBUS_NAME_UDISKS2
    properties_interface: str = DBUS_IFACE_DRIVE

    _nvme_controller: UDisks2NVMeController | None = None

    def __init__(self, object_path: str) -> None:
        """Initialize object."""
        self._object_path = object_path
        super().__init__()

    async def connect(self, bus: MessageBus) -> None:
        """Connect to bus."""
        await super().connect(bus)
        await self._reload_interfaces()

    @staticmethod
    async def new(object_path: str, bus: MessageBus) -> "UDisks2Drive":
        """Create and connect object."""
        obj = UDisks2Drive(object_path)
        await obj.connect(bus)
        return obj

    @property
    def object_path(self) -> str:
        """Object path for dbus object."""
        return self._object_path

    @property
    def nvme_controller(self) -> UDisks2NVMeController | None:
        """NVMe controller interface if drive is one."""
        return self._nvme_controller

    @property
    @dbus_property
    def vendor(self) -> str:
        """Return vendor name if known."""
        return self.properties[DBUS_ATTR_VENDOR]

    @property
    @dbus_property
    def model(self) -> str:
        """Return model name if known."""
        return self.properties[DBUS_ATTR_MODEL]

    @property
    @dbus_property
    def revision(self) -> str:
        """Return firmware revision."""
        return self.properties[DBUS_ATTR_REVISION]

    @property
    @dbus_property
    def serial(self) -> str:
        """Return serial number."""
        return self.properties[DBUS_ATTR_SERIAL]

    @property
    @dbus_property
    def wwn(self) -> str:
        """Return WWN (http://en.wikipedia.org/wiki/World_Wide_Name) if known."""
        return self.properties[DBUS_ATTR_WWN]

    @property
    @dbus_property
    def id(self) -> str:
        """Return unique and persistent id."""
        return self.properties[DBUS_ATTR_ID]

    @property
    @dbus_property
    def size(self) -> int:
        """Return drive size."""
        return self.properties[DBUS_ATTR_SIZE]

    @property
    @dbus_property
    def time_detected(self) -> datetime:
        """Return time drive first detected."""
        return datetime.fromtimestamp(
            self.properties[DBUS_ATTR_TIME_DETECTED] * 10**-6
        ).astimezone(UTC)

    @property
    @dbus_property
    def connection_bus(self) -> str:
        """Return physical connection bus used (usb, sdio, etc)."""
        return self.properties[DBUS_ATTR_CONNECTION_BUS]

    @property
    @dbus_property
    def seat(self) -> str:
        """Return seat drive is plugged into if any."""
        return self.properties[DBUS_ATTR_SEAT]

    @property
    @dbus_property
    def removable(self) -> bool:
        """Return true if drive is considered removable by user."""
        return self.properties[DBUS_ATTR_REMOVABLE]

    @property
    @dbus_property
    def ejectable(self) -> bool:
        """Return true if drive accepts an eject command."""
        return self.properties[DBUS_ATTR_EJECTABLE]

    @dbus_connected
    async def eject(self) -> None:
        """Eject media from drive."""
        await self.connected_dbus.Drive.call("eject", UDISKS2_DEFAULT_OPTIONS)

    @dbus_connected
    async def update(self, changed: dict[str, Any] | None = None) -> None:
        """Update properties via D-Bus."""
        await super().update(changed)

        if not changed and self.nvme_controller:
            await self.nvme_controller.update()

    @dbus_connected
    async def check_type(self) -> None:
        """Check if type of drive has changed and adjust interfaces if so."""
        introspection = await self.connected_dbus.introspect()
        interfaces = {intr.name for intr in introspection.interfaces}

        # If interfaces changed, update the proxy from introspection and reload interfaces
        if interfaces != set(self.connected_dbus.proxies.keys()):
            await self.connected_dbus.init_proxy(introspection=introspection)
            await self._reload_interfaces()

    @dbus_connected
    async def _reload_interfaces(self) -> None:
        """Reload interfaces from introspection as necessary."""
        # Check if drive is an nvme controller
        if (
            not self.nvme_controller
            and DBUS_IFACE_NVME_CONTROLLER in self.connected_dbus.proxies
        ):
            self._nvme_controller = UDisks2NVMeController(self.object_path)
            await self._nvme_controller.initialize(self.connected_dbus)

        elif (
            self.nvme_controller
            and DBUS_IFACE_NVME_CONTROLLER not in self.connected_dbus.proxies
        ):
            self.nvme_controller.stop_sync_property_changes()
            self._nvme_controller = None
