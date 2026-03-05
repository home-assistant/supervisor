"""Mock of OS Agent CGroup dbus service."""

from .base import DBusServiceMock, dbus_method

BUS_NAME = "io.hass.os"


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return CGroup()


class CGroup(DBusServiceMock):
    """CGroup mock.

    gdbus introspect --system --dest io.hass.os --object-path /io/hass/os/CGroup
    """

    object_path = "/io/hass/os/CGroup"
    interface = "io.hass.os.CGroup"

    @dbus_method()
    def AddDevicesAllowed(self, arg_0: "s", arg_1: "s") -> "b":
        """Load profile."""
        return True
