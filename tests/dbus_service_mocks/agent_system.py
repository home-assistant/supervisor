"""Mock of OS Agent System dbus service."""

from dbus_fast import DBusError

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
    response_schedule_wipe_device: bool | DBusError = True

    @dbus_method()
    def ScheduleWipeDevice(self) -> "b":
        """Schedule wipe device."""
        if isinstance(self.response_schedule_wipe_device, DBusError):
            raise self.response_schedule_wipe_device  # pylint: disable=raising-bad-type
        return self.response_schedule_wipe_device
