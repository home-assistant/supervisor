"""Mock of UDisks2 Filesystem service."""

from ctypes import c_uint64
from dataclasses import dataclass

from dbus_fast.service import PropertyAccess, dbus_property

from .base import DBusServiceMock, dbus_method

BUS_NAME = "org.freedesktop.UDisks2"
DEFAULT_OBJECT_PATH = "/org/freedesktop/UDisks2/block_devices/sda1"


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return Filesystem(object_path if object_path else DEFAULT_OBJECT_PATH)


@dataclass(slots=True)
class FilesystemFixture:
    """Filesystem fixture."""

    MountPoints: list[bytes]
    Size: c_uint64


FIXTURES: dict[str, FilesystemFixture] = {
    "/org/freedesktop/UDisks2/block_devices/mmcblk1p1": FilesystemFixture(
        MountPoints=[b"/mnt/boot"], Size=0
    ),
    "/org/freedesktop/UDisks2/block_devices/mmcblk1p3": FilesystemFixture(
        MountPoints=[
            b"/etc/NetworkManager/system-connections",
            b"/etc/dropbear",
            b"/etc/hostname",
            b"/etc/hosts",
            b"/etc/modprobe.d",
            b"/etc/modules-load.d",
            b"/etc/systemd/timesyncd.conf",
            b"/etc/udev/rules.d",
            b"/mnt/overlay",
            b"/root/.docker",
            b"/root/.ssh",
            b"/var/lib/NetworkManager",
            b"/var/lib/bluetooth",
            b"/var/lib/systemd",
        ],
        Size=100663296,
    ),
    "/org/freedesktop/UDisks2/block_devices/sda1": FilesystemFixture(
        MountPoints=[], Size=250058113024
    ),
    "/org/freedesktop/UDisks2/block_devices/sdb1": FilesystemFixture(
        MountPoints=[b"/mnt/data/supervisor/media/ext\x00"], Size=67108864
    ),
    "/org/freedesktop/UDisks2/block_devices/zram1": FilesystemFixture(
        MountPoints=[b"/var"], Size=0
    ),
}


class Filesystem(DBusServiceMock):
    """Filesystem mock.

    gdbus introspect --system --dest org.freedesktop.UDisks2 --object-path /org/freedesktop/UDisks2/block_devices/sda1
    """

    interface = "org.freedesktop.UDisks2.Filesystem"

    def __init__(self, object_path: str):
        """Initialize object."""
        super().__init__()
        self.object_path = object_path
        self.fixture: FilesystemFixture = FIXTURES[object_path]

    @dbus_property(access=PropertyAccess.READ)
    def MountPoints(self) -> "aay":
        """Get MountPoints."""
        return self.fixture.MountPoints

    @dbus_property(access=PropertyAccess.READ)
    def Size(self) -> "t":
        """Get Size."""
        return self.fixture.Size

    @dbus_method(track_obj_path=True)
    def SetLabel(self, label: "s", options: "a{sv}") -> None:
        """Do SetLabel method."""

    @dbus_method()
    def Mount(self, options: "a{sv}") -> "s":
        """Do Mount method."""
        return "/run/media/dev/hassos_data"

    @dbus_method()
    def Unmount(self, options: "a{sv}") -> None:
        """Do Unmount method."""

    @dbus_method()
    def Resize(self, size: "t", options: "a{sv}") -> None:
        """Do Resize method."""

    @dbus_method()
    def Check(self, options: "a{sv}") -> "b":
        """Do Check method."""
        return True

    @dbus_method()
    def Repair(self, options: "a{sv}") -> "b":
        """Do Repair method."""
        return True

    @dbus_method()
    def TakeOwnership(self, options: "a{sv}") -> None:
        """Do TakeOwnership method."""
