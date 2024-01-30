"""Mock of OS Agent Boards Supervised dbus service."""

from .base import DBusServiceMock

BUS_NAME = "io.hass.os"


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return Supervised()


class Supervised(DBusServiceMock):
    """Supervised mock.

    gdbus introspect --system --dest io.hass.os --object-path /io/hass/os/Boards/Supervised
    """

    object_path = "/io/hass/os/Boards/Supervised"
    interface = "io.hass.os.Boards.Supervised"
