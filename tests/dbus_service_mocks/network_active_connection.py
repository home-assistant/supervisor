"""Mock of Network Manager Active Connection service."""

from dbus_fast.service import PropertyAccess, dbus_property, signal

from .base import DBusServiceMock

BUS_NAME = "org.freedesktop.NetworkManager"


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return ActiveConnection()


# pylint: disable=invalid-name


class ActiveConnection(DBusServiceMock):
    """Active Connection mock.

    gdbus introspect --system --dest org.freedesktop.NetworkManager --object-path /org/freedesktop/NetworkManager/ActiveConnection/1
    """

    interface = "org.freedesktop.NetworkManager.Connection.Active"
    object_path = "/org/freedesktop/NetworkManager/ActiveConnection/1"

    @dbus_property(access=PropertyAccess.READ)
    def Connection(self) -> "o":
        """Get Connection."""
        return "/org/freedesktop/NetworkManager/Settings/1"

    @dbus_property(access=PropertyAccess.READ)
    def SpecificObject(self) -> "o":
        """Get SpecificObject."""
        return "/"

    @dbus_property(access=PropertyAccess.READ)
    def Id(self) -> "s":
        """Get Id."""
        return "Wired connection 1"

    @dbus_property(access=PropertyAccess.READ)
    def Uuid(self) -> "s":
        """Get Uuid."""
        return "0c23631e-2118-355c-bbb0-8943229cb0d6"

    @dbus_property(access=PropertyAccess.READ)
    def Type(self) -> "s":
        """Get Type."""
        return "802-3-ethernet"

    @dbus_property(access=PropertyAccess.READ)
    def Devices(self) -> "ao":
        """Get Devices."""
        return ["/org/freedesktop/NetworkManager/Devices/1"]

    @dbus_property(access=PropertyAccess.READ)
    def State(self) -> "u":
        """Get State."""
        return 2

    @dbus_property(access=PropertyAccess.READ)
    def StateFlags(self) -> "u":
        """Get StateFlags."""
        return 92

    @dbus_property(access=PropertyAccess.READ)
    def Default(self) -> "b":
        """Get Default."""
        return True

    @dbus_property(access=PropertyAccess.READ)
    def Ip4Config(self) -> "o":
        """Get Ip4Config."""
        return "/org/freedesktop/NetworkManager/IP4Config/1"

    @dbus_property(access=PropertyAccess.READ)
    def Dhcp4Config(self) -> "o":
        """Get Dhcp4Config."""
        return "/org/freedesktop/NetworkManager/DHCP4Config/1"

    @dbus_property(access=PropertyAccess.READ)
    def Default6(self) -> "b":
        """Get Default6."""
        return False

    @dbus_property(access=PropertyAccess.READ)
    def Ip6Config(self) -> "o":
        """Get Ip6Config."""
        return "/org/freedesktop/NetworkManager/IP6Config/1"

    @dbus_property(access=PropertyAccess.READ)
    def Dhcp6Config(self) -> "o":
        """Get Dhcp6Config."""
        return "/"

    @dbus_property(access=PropertyAccess.READ)
    def Vpn(self) -> "b":
        """Get Vpn."""
        return False

    @dbus_property(access=PropertyAccess.READ)
    def Master(self) -> "o":
        """Get Master."""
        return "/"

    @signal()
    def StateChanged(self) -> "uu":
        """Signal StateChanged."""
        return [2, 0]
