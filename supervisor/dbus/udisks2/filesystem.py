"""Interface to UDisks2 Filesystem over D-Bus."""

from pathlib import Path

from ..const import (
    DBUS_ATTR_MOUNT_POINTS,
    DBUS_ATTR_SIZE,
    DBUS_IFACE_FILESYSTEM,
    DBUS_NAME_UDISKS2,
)
from ..interface import DBusInterfaceProxy, dbus_property
from ..utils import dbus_connected
from .const import UDISKS2_DEFAULT_OPTIONS
from .data import MountOptions, UnmountOptions, udisks2_bytes_to_path


class UDisks2Filesystem(DBusInterfaceProxy):
    """Handle D-Bus interface for UDisks2 filesystem device object.

    http://storaged.org/doc/udisks2-api/latest/gdbus-org.freedesktop.UDisks2.Filesystem.html
    """

    name: str = DBUS_IFACE_FILESYSTEM
    bus_name: str = DBUS_NAME_UDISKS2
    properties_interface: str = DBUS_IFACE_FILESYSTEM

    def __init__(self, object_path: str, *, sync_properties: bool = True) -> None:
        """Initialize object."""
        self._object_path = object_path
        self.sync_properties = sync_properties
        super().__init__()

    @property
    def object_path(self) -> str:
        """Object path for dbus object."""
        return self._object_path

    @property
    @dbus_property
    def mount_points(self) -> list[Path]:
        """Return mount points."""
        return [
            udisks2_bytes_to_path(mount_point)
            for mount_point in self.properties[DBUS_ATTR_MOUNT_POINTS]
        ]

    @property
    @dbus_property
    def size(self) -> int:
        """Return size."""
        return self.properties[DBUS_ATTR_SIZE]

    @dbus_connected
    async def mount(self, options: MountOptions | None = None) -> str:
        """Mount filesystem.

        Caller cannot provide mountpoint. UDisks selects a folder within /run/media/$USER
        if not overridden in /etc/fstab. Therefore unclear if this can be useful to supervisor.
        http://storaged.org/doc/udisks2-api/latest/gdbus-org.freedesktop.UDisks2.Filesystem.html#gdbus-method-org-freedesktop-UDisks2-Filesystem.Mount
        """
        mount_options = options.to_dict() if options else {}
        return await self.connected_dbus.Filesystem.call(
            "mount", mount_options | UDISKS2_DEFAULT_OPTIONS
        )

    @dbus_connected
    async def unmount(self, options: UnmountOptions | None = None) -> None:
        """Unmount filesystem."""
        unmount_options = options.to_dict() if options else {}
        await self.connected_dbus.Filesystem.call(
            "unmount", unmount_options | UDISKS2_DEFAULT_OPTIONS
        )

    @dbus_connected
    async def set_label(self, label: str) -> None:
        """Set filesystem label."""
        await self.connected_dbus.Filesystem.call(
            "set_label", label, UDISKS2_DEFAULT_OPTIONS
        )

    @dbus_connected
    async def check(self) -> bool:
        """Check filesystem for consistency. Returns true if it passed."""
        return await self.connected_dbus.Filesystem.call(
            "check", UDISKS2_DEFAULT_OPTIONS
        )

    @dbus_connected
    async def repair(self) -> bool:
        """Attempt to repair filesystem. Returns true if repair was successful."""
        return await self.connected_dbus.Filesystem.call(
            "repair", UDISKS2_DEFAULT_OPTIONS
        )
