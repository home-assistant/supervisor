"""Mock of logind dbus service."""

from .base import DBusServiceMock, dbus_method

BUS_NAME = "org.freedesktop.login1"


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return Logind()


class Logind(DBusServiceMock):
    """Logind mock.

    gdbus introspect --system --dest org.freedesktop.login1 --object-path /org/freedesktop/login1
    """

    object_path = "/org/freedesktop/login1"
    interface = "org.freedesktop.login1.Manager"

    @dbus_method()
    def Reboot(self, interactive: "b") -> None:
        """Reboot."""

    @dbus_method()
    def PowerOff(self, interactive: "b") -> None:
        """PowerOff."""
