"""DataDisk object for OS-Agent."""

from pathlib import Path

from ..const import (
    DBUS_ATTR_CURRENT_DEVICE,
    DBUS_IFACE_HAOS_DATADISK,
    DBUS_NAME_HAOS,
    DBUS_OBJECT_HAOS_DATADISK,
)
from ..interface import DBusInterfaceProxy, dbus_property
from ..utils import dbus_connected


class DataDisk(DBusInterfaceProxy):
    """DataDisk object for OS Agent."""

    bus_name: str = DBUS_NAME_HAOS
    object_path: str = DBUS_OBJECT_HAOS_DATADISK
    properties_interface: str = DBUS_IFACE_HAOS_DATADISK

    @property
    @dbus_property
    def current_device(self) -> Path:
        """Return current device used for data."""
        return Path(self.properties[DBUS_ATTR_CURRENT_DEVICE])

    @dbus_connected
    async def change_device(self, device: Path) -> None:
        """Migrate data disk to a new device."""
        await self.connected_dbus.DataDisk.call("change_device", device.as_posix())

    @dbus_connected
    async def reload_device(self) -> None:
        """Reload device data."""
        await self.connected_dbus.DataDisk.call("reload_device")

    @dbus_connected
    async def mark_data_move(self) -> None:
        """Create marker to signal to do data disk migration next reboot."""
        await self.connected_dbus.DataDisk.call("mark_data_move")
