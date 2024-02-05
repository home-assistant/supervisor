"""Mock of OS Agent System dbus service."""

from .base import DBusServiceMock, dbus_method

BUS_NAME = "io.hass.os"


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return System()


class System(DBusServiceMock):
    """System mock.

    gdbus introspect --system --dest io.hass.os --object-path /io/hass/os/System
    """

    object_path = "/io/hass/os/System"
    interface = "io.hass.os.System"

    @dbus_method()
    def ScheduleWipeDevice(self) -> "b":
        """Schedule wipe device."""
        return True

    @dbus_method()
    def WipeDevice(self) -> "b":
        """Wipe device."""
        return True
