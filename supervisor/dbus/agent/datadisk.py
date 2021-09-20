"""DataDisk object for OS-Agent."""
from pathlib import Path
from typing import Any, Dict

from ...utils.gdbus import DBus
from ..const import (
    DBUS_ATTR_CURRENT_DEVICE,
    DBUS_NAME_HAOS,
    DBUS_NAME_HAOS_DATADISK,
    DBUS_OBJECT_HAOS_DATADISK,
)
from ..interface import DBusInterface, dbus_property
from ..utils import dbus_connected


class DataDisk(DBusInterface):
    """DataDisk object for OS Agent."""

    def __init__(self) -> None:
        """Initialize Properties."""
        self.properties: Dict[str, Any] = {}

    @property
    @dbus_property
    def current_device(self) -> Path:
        """Return current device used for data."""
        return Path(self.properties[DBUS_ATTR_CURRENT_DEVICE])

    async def connect(self) -> None:
        """Get connection information."""
        self.dbus = await DBus.connect(DBUS_NAME_HAOS, DBUS_OBJECT_HAOS_DATADISK)

    @dbus_connected
    async def update(self):
        """Update Properties."""
        self.properties = await self.dbus.get_properties(DBUS_NAME_HAOS_DATADISK)

    @dbus_connected
    async def change_device(self, device: Path) -> None:
        """Migrate data disk to a new device."""
        await self.dbus.DataDisk.ChangeDevice(device.as_posix())

    @dbus_connected
    async def reload_device(self) -> None:
        """Reload device data."""
        await self.dbus.DataDisk.ReloadDevice()
