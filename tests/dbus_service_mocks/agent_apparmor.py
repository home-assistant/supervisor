"""Mock of OS Agent AppArmor dbus service."""

from dbus_fast.service import PropertyAccess, dbus_property

from .base import DBusServiceMock, dbus_method

BUS_NAME = "io.hass.os"


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return AppArmor()


class AppArmor(DBusServiceMock):
    """AppArmor mock.

    gdbus introspect --system --dest io.hass.os --object-path /io/hass/os/AppArmor
    """

    object_path = "/io/hass/os/AppArmor"
    interface = "io.hass.os.AppArmor"

    @dbus_property(access=PropertyAccess.READ)
    def ParserVersion(self) -> "s":
        """Get ParserVersion."""
        return "2.13.2"

    @dbus_method()
    def LoadProfile(self, arg_0: "s", arg_1: "s") -> "b":
        """Load profile."""
        return True

    @dbus_method()
    def UnloadProfile(self, arg_0: "s", arg_1: "s") -> "b":
        """Unload profile."""
        return True
