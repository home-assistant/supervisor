"""Mock of OS Agent Timesyncd dbus service."""

from dbus_fast.service import dbus_property

from .base import DBusServiceMock

BUS_NAME = "io.hass.os"


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return Timesyncd()


class Timesyncd(DBusServiceMock):
    """Timesyncd mock.

    gdbus introspect --system --dest io.hass.os --object-path /io/hass/os/Config/Timesyncd
    """

    object_path = "/io/hass/os/Config/Timesyncd"
    interface = "io.hass.os.Config.Timesyncd"

    def __init__(self) -> None:
        """Initialize mock."""
        super().__init__()
        self.ntp_server = ["time.cloudflare.com"]
        self.fallback_ntp_server = ["time.google.com"]

    @dbus_property()
    def FallbackNTPServer(self) -> "as":
        """Get fallback NTP servers."""
        return self.fallback_ntp_server

    @FallbackNTPServer.setter
    def FallbackNTPServer(self, value: "as"):
        """Set fallback NTP servers."""
        self.fallback_ntp_server = value
        self.emit_properties_changed({"FallbackNTPServer": value})

    @dbus_property()
    def NTPServer(self) -> "as":
        """Get NTP servers."""
        return self.ntp_server

    @NTPServer.setter
    def NTPServer(self, value: "as"):
        """Set NTP servers."""
        self.ntp_server = value
        self.emit_properties_changed({"NTPServer": value})
