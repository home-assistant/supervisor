"""Interface to UDisks2 Filesystem over D-Bus."""
from dataclasses import dataclass
from typing import Dict, Optional

from dbus_next.signature import Variant

from . import UDisks2StandardOptions, UDisks2StandardOptionsDataType
from ..const import DBUS_ATTR_MOUNTPOINTS, DBUS_ATTR_SIZE, DBUS_IFACE_FILESYSTEM
from ..interface import dbus_property
from ..utils import dbus_connected
from .block import UDisks2Block


class MountOptionsDataType(UDisks2StandardOptionsDataType, total=False):
    """Filesystem mount/unmount options data type."""

    fstype: str
    options: str


@dataclass
class MountOptions(UDisks2StandardOptions):
    """Filesystem mount/unmount options."""

    fstype: str | None
    options: str | None

    @staticmethod
    def from_dict(data: MountOptionsDataType) -> "MountOptions":
        """Create MountOptions from dict."""
        return MountOptions(
            auth_no_user_interaction=data.get("auth.no_user_interaction"),
            fstype=data.get("fstype"),
            options=data.get("options"),
        )

    def to_dict(self) -> Dict[str, Variant]:
        """Return dict representation."""
        data = {
            "auth.no_user_interaction": Variant("b", self.auth_no_user_interaction),
            "fstype": Variant("s", self.fstype),
            "options": Variant("s", self.options),
        }
        return {k: v for k, v in data.items() if v.value is not None}


class UDisks2Filesystem(UDisks2Block):
    """Handle D-Bus interface for UDisks2 filesystem device object.

    http://storaged.org/doc/udisks2-api/latest/gdbus-org.freedesktop.UDisks2.Filesystem.html
    """

    properties_interface: str = DBUS_IFACE_FILESYSTEM

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
    async def mount(self, options: Optional[MountOptions] = None) -> None:
        """Mount filesystem."""
        await self.dbus.Filesystem.call_mount(options.to_dict() if options else {})

    @dbus_connected
    async def unmount(self, options: Optional[MountOptions] = None) -> None:
        """Unmount filesystem."""
        await self.dbus.Filesystem.call_unmount(options.to_dict() if options else {})
