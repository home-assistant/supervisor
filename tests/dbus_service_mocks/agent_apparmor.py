"""Mock of OS Agent AppArmor dbus service."""

from dbus_fast import DBusError
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
    response_load_profile: bool | DBusError = True
    response_unload_profile: bool | DBusError = True

    @dbus_property(access=PropertyAccess.READ)
    def ParserVersion(self) -> "s":
        """Get ParserVersion."""
        return "2.13.2"

    @dbus_method()
    def LoadProfile(self, arg_0: "s", arg_1: "s") -> "b":
        """Load profile."""
        if isinstance(self.response_load_profile, DBusError):
            raise self.response_load_profile  # pylint: disable=raising-bad-type
        return self.response_load_profile

    @dbus_method()
    def UnloadProfile(self, arg_0: "s", arg_1: "s") -> "b":
        """Unload profile."""
        if isinstance(self.response_unload_profile, DBusError):
            raise self.response_unload_profile  # pylint: disable=raising-bad-type
        return self.response_unload_profile
