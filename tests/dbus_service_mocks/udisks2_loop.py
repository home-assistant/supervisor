"""Mock of UDisks2 Loop service."""

from dbus_fast.service import PropertyAccess, dbus_property

from .base import DBusServiceMock, dbus_method

BUS_NAME = "org.freedesktop.UDisks2"


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return Loop()


class Loop(DBusServiceMock):
    """Loop mock.

    gdbus introspect --system --dest org.freedesktop.UDisks2 --object-path /org/freedesktop/UDisks2/block_devices/loop0
    """

    interface = "org.freedesktop.UDisks2.Loop"
    object_path = "/org/freedesktop/UDisks2/block_devices/loop0"

    @dbus_property(access=PropertyAccess.READ)
    def BackingFile(self) -> "ay":
        """Get BackingFile."""
        return b""

    @dbus_property(access=PropertyAccess.READ)
    def Autoclear(self) -> "b":
        """Get Autoclear."""
        return False

    @dbus_property(access=PropertyAccess.READ)
    def SetupByUID(self) -> "u":
        """Get SetupByUID."""
        return 0

    @dbus_method()
    def Delete(self, options: "a{sv}") -> None:
        """Do Delete method."""

    @dbus_method()
    def SetAutoClear(self, value: "b", options: "a{sv}") -> None:
        """Do SetAutoClear method."""
