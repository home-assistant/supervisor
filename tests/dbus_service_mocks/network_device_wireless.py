"""Mock of Network Manager Device Wireless service."""

from dbus_fast.service import PropertyAccess, dbus_property, signal

from .base import DBusServiceMock, dbus_method

BUS_NAME = "org.freedesktop.NetworkManager"


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return DeviceWireless()


class DeviceWireless(DBusServiceMock):
    """Device Wireless mock.

    gdbus introspect --system --dest org.freedesktop.NetworkManager --object-path /org/freedesktop/NetworkManager/Devices/1
    """

    interface = "org.freedesktop.NetworkManager.Device.Wireless"
    object_path = "/org/freedesktop/NetworkManager/Devices/3"
    all_access_points = [
        "/org/freedesktop/NetworkManager/AccessPoint/43099",
        "/org/freedesktop/NetworkManager/AccessPoint/43100",
    ]

    @dbus_property(access=PropertyAccess.READ)
    def HwAddress(self) -> "s":
        """Get HwAddress."""
        return "EA:3C:50:4C:B8:82"

    @dbus_property(access=PropertyAccess.READ)
    def PermHwAddress(self) -> "s":
        """Get PermHwAddress."""
        return "DC:A6:32:02:BA:21"

    @dbus_property(access=PropertyAccess.READ)
    def Mode(self) -> "u":
        """Get Mode."""
        return 2

    @dbus_property(access=PropertyAccess.READ)
    def Bitrate(self) -> "u":
        """Get Bitrate."""
        return 0

    @dbus_property(access=PropertyAccess.READ)
    def AccessPoints(self) -> "ao":
        """Get AccessPoints."""
        return [
            "/org/freedesktop/NetworkManager/AccessPoint/41533",
            "/org/freedesktop/NetworkManager/AccessPoint/41534",
            "/org/freedesktop/NetworkManager/AccessPoint/41535",
            "/org/freedesktop/NetworkManager/AccessPoint/41536",
            "/org/freedesktop/NetworkManager/AccessPoint/41537",
            "/org/freedesktop/NetworkManager/AccessPoint/41538",
            "/org/freedesktop/NetworkManager/AccessPoint/41539",
            "/org/freedesktop/NetworkManager/AccessPoint/41540",
            "/org/freedesktop/NetworkManager/AccessPoint/41541",
        ]

    @dbus_property(access=PropertyAccess.READ)
    def ActiveAccessPoint(self) -> "o":
        """Get ActiveAccessPoint."""
        return "/"

    @dbus_property(access=PropertyAccess.READ)
    def WirelessCapabilities(self) -> "u":
        """Get WirelessCapabilities."""
        return 2047

    @dbus_property(access=PropertyAccess.READ)
    def LastScan(self) -> "x":
        """Get LastScan."""
        return 1343924585

    @signal()
    def AccessPointAdded(self) -> "o":
        """Signal AccessPointAdded."""
        return "/org/freedesktop/NetworkManager/AccessPoint/43100"

    @signal()
    def AccessPointRemoved(self) -> "o":
        """Signal AccessPointRemoved."""
        return "/org/freedesktop/NetworkManager/AccessPoint/43100"

    @dbus_method()
    def GetAccessPoints(self) -> "ao":
        """Do GetAccessPoints method."""
        return self.GetAllAccessPoints()

    @dbus_method()
    def GetAllAccessPoints(self) -> "ao":
        """Do GetAllAccessPoints method."""
        return self.all_access_points

    @dbus_method()
    def RequestScan(self, options: "a{sv}") -> None:
        """Do RequestScan method."""
