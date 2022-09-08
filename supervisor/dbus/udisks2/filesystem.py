"""Interface to UDisks2 Filesystem over D-Bus."""
from typing import Any
from ..const import (
    DBUS_ATTR_MOUNTPOINTS,
    DBUS_ATTR_SIZE,
    DBUS_IFACE_FILESYSTEM,
)
from ..interface import dbus_property
from ..utils import dbus_connected
from .block import UDisks2Block


class UDisks2Filesystem(UDisks2Block):
    """Filesystem device object for UDisks2."""

    @property
    @dbus_property
    def mountpoints(self) -> str:
        """Return mountpoints."""
        return [
            bytes(mountpoint).decode()
            for mountpoint in self.properties[DBUS_ATTR_MOUNTPOINTS]
        ]

    @property
    @dbus_property
    def size(self) -> int:
        """Return size."""
        return self.properties[DBUS_ATTR_SIZE]

    @dbus_connected
    async def mount(self, options: dict[str, Any]):
        """Mount filesystem."""
        await self.dbus.Filesystem.Mount(("a{sv}", options))

    @dbus_connected
    async def unmount(self, options: dict[str, Any]):
        """Unmount filesystem."""
        await self.dbus.Filesystem.Unmount(("a{sv}", options))

    @dbus_connected
    async def update(self):
        """Update Properties."""
        self.properties = {}
        await super().update()
        self.properties.update(await self.dbus.get_properties(DBUS_IFACE_FILESYSTEM))
