"""Mock of os agent dbus service."""

from dbus_fast.service import PropertyAccess, dbus_property

from .base import DBusServiceMock

BUS_NAME = "io.hass.os"


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return OSAgent()


class OSAgent(DBusServiceMock):
    """OS-agent mock.

    gdbus introspect --system --dest io.hass.os --object-path /io/hass/os
    """

    object_path = "/io/hass/os"
    interface = "io.hass.os"

    @dbus_property(access=PropertyAccess.READ)
    def Version(self) -> "s":
        """Get Version."""
        return "1.1.0"

    @dbus_property()
    def Diagnostics(self) -> "b":
        """Get Diagnostics."""
        return True

    @Diagnostics.setter
    def Diagnostics(self, value: "b"):
        """Set Diagnostics."""
        self.emit_properties_changed({"Diagnostics": value})
