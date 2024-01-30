"""Mock of Network Manager DNS Manager service."""

from dbus_fast import Variant
from dbus_fast.service import PropertyAccess, dbus_property

from .base import DBusServiceMock

BUS_NAME = "org.freedesktop.NetworkManager"


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return DnsManager()


class DnsManager(DBusServiceMock):
    """DNS Manager mock.

    gdbus introspect --system --dest org.freedesktop.NetworkManager --object-path /org/freedesktop/NetworkManager/DnsManager
    """

    interface = "org.freedesktop.NetworkManager.DnsManager"
    object_path = "/org/freedesktop/NetworkManager/DnsManager"

    @dbus_property(access=PropertyAccess.READ)
    def Mode(self) -> "s":
        """Get Mode."""
        return "default"

    @dbus_property(access=PropertyAccess.READ)
    def RcManager(self) -> "s":
        """Get RcManager."""
        return "file"

    @dbus_property(access=PropertyAccess.READ)
    def Configuration(self) -> "aa{sv}":
        """Get Configuration."""
        return [
            {
                "nameservers": Variant("as", ["192.168.30.1"]),
                "domains": Variant("as", ["syshack.ch"]),
                "interface": Variant("s", "eth0"),
                "priority": Variant("i", 100),
                "vpn": Variant("b", False),
            }
        ]
