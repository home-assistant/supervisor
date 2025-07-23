"""Mock of OS Agent DataDisk dbus service."""

from dbus_fast.service import PropertyAccess, dbus_property

from .base import DBusServiceMock, dbus_method

BUS_NAME = "io.hass.os"


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return DataDisk()


class DataDisk(DBusServiceMock):
    """DataDisk mock.

    gdbus introspect --system --dest io.hass.os --object-path /io/hass/os/DataDisk
    """

    object_path = "/io/hass/os/DataDisk"
    interface = "io.hass.os.DataDisk"
    current_device = "/dev/mmcblk1"

    @dbus_property(access=PropertyAccess.READ)
    def CurrentDevice(self) -> "s":
        """Get Current Device."""
        return self.current_device

    @dbus_method()
    def ChangeDevice(self, arg_0: "s") -> "b":
        """Change device."""
        return True

    @dbus_method()
    def ReloadDevice(self) -> "b":
        """Reload device."""
        return True

    @dbus_method()
    def MarkDataMove(self) -> None:
        """Do MarkDataMove method."""
