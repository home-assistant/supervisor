"""Mock of OS Agent Swap dbus service."""

from dbus_fast.service import dbus_property

from .base import DBusServiceMock

BUS_NAME = "io.hass.os"


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return Swap()


class Swap(DBusServiceMock):
    """Swap mock.

    gdbus introspect --system --dest io.hass.os --object-path /io/hass/os/Config/Swap
    """

    object_path = "/io/hass/os/Config/Swap"
    interface = "io.hass.os.Config.Swap"

    @dbus_property()
    def SwapSize(self) -> "s":
        """Get swap size."""
        return "1M"

    @SwapSize.setter
    def SwapSize(self, value: "s"):
        """Set swap size."""
        self.emit_properties_changed({"SwapSize": value})

    @dbus_property()
    def Swappiness(self) -> "i":
        """Get swappiness."""
        return 1

    @Swappiness.setter
    def Swappiness(self, value: "i"):
        """Set swappiness."""
        self.emit_properties_changed({"Swappiness": value})
