"""Mock of OS Agent Boards Yellow dbus service."""

from dbus_fast.service import dbus_property

from .base import DBusServiceMock

BUS_NAME = "io.hass.os"


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return Yellow()


class Yellow(DBusServiceMock):
    """Yellow mock.

    gdbus introspect --system --dest io.hass.os --object-path /io/hass/os/Boards/Yellow
    """

    object_path = "/io/hass/os/Boards/Yellow"
    interface = "io.hass.os.Boards.Yellow"

    @dbus_property()
    def HeartbeatLED(self) -> "b":
        """Get Heartbeat LED."""
        return True

    @HeartbeatLED.setter
    def HeartbeatLED(self, value: "b"):
        """Set Heartbeat LED."""
        self.emit_properties_changed({"HeartbeatLED": value})

    @dbus_property()
    def PowerLED(self) -> "b":
        """Get Power LED."""
        return True

    @PowerLED.setter
    def PowerLED(self, value: "b"):
        """Set Power LED."""
        self.emit_properties_changed({"PowerLED": value})

    @dbus_property()
    def DiskLED(self) -> "b":
        """Get Disk LED."""
        return True

    @DiskLED.setter
    def DiskLED(self, value: "b"):
        """Set Disk LED."""
        self.emit_properties_changed({"DiskLED": value})
