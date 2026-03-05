"""Mock of Network Manager IP4Config service."""

from dbus_fast import Variant
from dbus_fast.service import PropertyAccess, dbus_property

from .base import DBusServiceMock

BUS_NAME = "org.freedesktop.NetworkManager"


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return IP4Config()


class IP4Config(DBusServiceMock):
    """IP4Config mock.

    gdbus introspect --system --dest org.freedesktop.NetworkManager --object-path /org/freedesktop/NetworkManager/IP4Config/1
    """

    interface = "org.freedesktop.NetworkManager.IP4Config"
    object_path = "/org/freedesktop/NetworkManager/IP4Config/1"

    @dbus_property(access=PropertyAccess.READ)
    def Addresses(self) -> "aau":
        """Get Addresses."""
        return [[2499979456, 24, 16951488]]

    @dbus_property(access=PropertyAccess.READ)
    def AddressData(self) -> "aa{sv}":
        """Get AddressData."""
        return [{"address": Variant("s", "192.168.2.148"), "prefix": Variant("u", 24)}]

    @dbus_property(access=PropertyAccess.READ)
    def Gateway(self) -> "s":
        """Get Gateway."""
        return "192.168.2.1"

    @dbus_property(access=PropertyAccess.READ)
    def Routes(self) -> "aau":
        """Get Routes."""
        return [[174272, 24, 0, 100], [65193, 16, 0, 1000]]

    @dbus_property(access=PropertyAccess.READ)
    def RouteData(self) -> "aa{sv}":
        """Get RouteData."""
        return [
            {
                "dest": Variant("s", "192.168.2.0"),
                "prefix": Variant("u", 24),
                "metric": Variant("u", 100),
            },
            {
                "dest": Variant("s", "169.254.0.0"),
                "prefix": Variant("u", 16),
                "metric": Variant("u", 1000),
            },
            {
                "dest": Variant("s", "0.0.0.0"),
                "prefix": Variant("u", 0),
                "next-hop": Variant("s", "192.168.2.1"),
                "metric": Variant("u", 100),
            },
        ]

    @dbus_property(access=PropertyAccess.READ)
    def NameserverData(self) -> "aa{sv}":
        """Get NameserverData."""
        return [{"address": Variant("s", "192.168.2.2")}]

    @dbus_property(access=PropertyAccess.READ)
    def Nameservers(self) -> "au":
        """Get Nameservers."""
        return [16951488]

    @dbus_property(access=PropertyAccess.READ)
    def Domains(self) -> "as":
        """Get Domains."""
        return []

    @dbus_property(access=PropertyAccess.READ)
    def Searches(self) -> "as":
        """Get Searches."""
        return []

    @dbus_property(access=PropertyAccess.READ)
    def DnsOptions(self) -> "as":
        """Get DnsOptions."""
        return []

    @dbus_property(access=PropertyAccess.READ)
    def DnsPriority(self) -> "i":
        """Get DnsPriority."""
        return 100

    @dbus_property(access=PropertyAccess.READ)
    def WinsServerData(self) -> "as":
        """Get WinsServerData."""
        return []

    @dbus_property(access=PropertyAccess.READ)
    def WinsServers(self) -> "au":
        """Get WinsServers."""
        return []
