"""Mock of OS Agent Boards Green dbus service."""

from dbus_fast.service import dbus_property

from .base import DBusServiceMock

BUS_NAME = "io.hass.os"


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return Green()


class Green(DBusServiceMock):
    """Green mock.

    gdbus introspect --system --dest io.hass.os --object-path /io/hass/os/Boards/Green
    """

    object_path = "/io/hass/os/Boards/Green"
    interface = "io.hass.os.Boards.Green"

    @dbus_property()
    def ActivityLED(self) -> "b":
        """Get Activity LED."""
        return True

    @ActivityLED.setter
    def ActivityLED(self, value: "b"):
        """Set Activity LED."""
        self.emit_properties_changed({"ActivityLED": value})

    @dbus_property()
    def PowerLED(self) -> "b":
        """Get Power LED."""
        return True

    @PowerLED.setter
    def PowerLED(self, value: "b"):
        """Set Power LED."""
        self.emit_properties_changed({"PowerLED": value})

    @dbus_property()
    def UserLED(self) -> "b":
        """Get User LED."""
        return True

    @UserLED.setter
    def UserLED(self, value: "b"):
        """Set User LED."""
        self.emit_properties_changed({"UserLED": value})
