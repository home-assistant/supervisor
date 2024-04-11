"""Mock of UDisks2 Manager service."""

from dbus_fast.service import PropertyAccess, dbus_property

from .base import DBusServiceMock, dbus_method

BUS_NAME = "org.freedesktop.UDisks2"


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return UDisks2Manager()


class UDisks2Manager(DBusServiceMock):
    """UDisks2 Manager mock.

    gdbus introspect --system --dest org.freedesktop.UDisks2 --object-path /org/freedesktop/UDisks2/Manager
    """

    interface = "org.freedesktop.UDisks2.Manager"
    object_path = "/org/freedesktop/UDisks2/Manager"
    block_devices = [
        "/org/freedesktop/UDisks2/block_devices/loop0",
        "/org/freedesktop/UDisks2/block_devices/mmcblk1",
        "/org/freedesktop/UDisks2/block_devices/mmcblk1p1",
        "/org/freedesktop/UDisks2/block_devices/mmcblk1p2",
        "/org/freedesktop/UDisks2/block_devices/mmcblk1p3",
        "/org/freedesktop/UDisks2/block_devices/sda",
        "/org/freedesktop/UDisks2/block_devices/sda1",
        "/org/freedesktop/UDisks2/block_devices/sdb",
        "/org/freedesktop/UDisks2/block_devices/sdb1",
        "/org/freedesktop/UDisks2/block_devices/zram1",
    ]
    resolved_devices: list[list[str]] | list[str] = [
        "/org/freedesktop/UDisks2/block_devices/sda1"
    ]

    @dbus_property(access=PropertyAccess.READ)
    def Version(self) -> "s":
        """Get Version."""
        return "2.9.2"

    @dbus_property(access=PropertyAccess.READ)
    def SupportedFilesystems(self) -> "as":
        """Get SupportedFilesystems."""
        return ["ext4", "vfat", "ntfs", "exfat", "swap"]

    @dbus_property(access=PropertyAccess.READ)
    def SupportedEncryptionTypes(self) -> "as":
        """Get SupportedEncryptionTypes."""
        return ["luks1", "luks2"]

    @dbus_property(access=PropertyAccess.READ)
    def DefaultEncryptionType(self) -> "s":
        """Get DefaultEncryptionType."""
        return "luks1"

    @dbus_method()
    def CanFormat(self, type_: "s") -> "(bs)":
        """Do CanFormat method."""
        return [False, "mkfs.ntfs"]

    @dbus_method()
    def CanResize(self, type_: "s") -> "(bts)":
        """Do CanResize method."""
        return [False, 6, "ntfsresize"]

    @dbus_method()
    def CanCheck(self, type_: "s") -> "(bs)":
        """Do CanCheck method."""
        return [False, "ntfsfix"]

    @dbus_method()
    def CanRepair(self, type_: "s") -> "(bs)":
        """Do CanRepair method."""
        return [False, "ntfsfix"]

    @dbus_method()
    def LoopSetup(self, fd: "h", options: "a{sv}") -> "o":
        """Do LoopSetup method."""
        return "/org/freedesktop/UDisks2/block_devices/loop0"

    @dbus_method()
    def MDRaidCreate(
        self, blocks: "ao", level: "s", name: "s", chunk: "t", options: "a{sv}"
    ) -> "o":
        """Do MDRaidCreate method."""
        return "/org/freedesktop/UDisks2/block_devices/sdb"

    @dbus_method()
    def EnableModule(self, name: "s", enable: "b") -> None:
        """Do EnableModule method."""

    @dbus_method()
    def GetBlockDevices(self, options: "a{sv}") -> "ao":
        """Do GetBlockDevices method."""
        return self.block_devices

    @dbus_method()
    def ResolveDevice(self, devspec: "a{sv}", options: "a{sv}") -> "ao":
        """Do ResolveDevice method."""
        if len(self.resolved_devices) > 0 and isinstance(
            self.resolved_devices[0], list
        ):
            return self.resolved_devices.pop(0)
        return self.resolved_devices
