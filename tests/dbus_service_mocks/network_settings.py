"""Mock of Network Manager Settings service."""

from dbus_fast.service import PropertyAccess, dbus_property, signal

from .base import DBusServiceMock, dbus_method

BUS_NAME = "org.freedesktop.NetworkManager"


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return Settings()


class Settings(DBusServiceMock):
    """Settings mock.

    gdbus introspect --system --dest org.freedesktop.NetworkManager --object-path /org/freedesktop/NetworkManager/Settings
    """

    interface = "org.freedesktop.NetworkManager.Settings"
    object_path = "/org/freedesktop/NetworkManager/Settings"

    @dbus_property(access=PropertyAccess.READ)
    def Connections(self) -> "ao":
        """Get Connections."""
        return ["/org/freedesktop/NetworkManager/Settings/1"]

    @dbus_property(access=PropertyAccess.READ)
    def Hostname(self) -> "s":
        """Get Hostname."""
        return "homeassistant"

    @dbus_property(access=PropertyAccess.READ)
    def CanModify(self) -> "b":
        """Get CanModify."""
        return True

    @signal()
    def NewConnection(self) -> "o":
        """Signal NewConnection."""
        return "/org/freedesktop/NetworkManager/Settings/1"

    @signal()
    def ConnectionRemoved(self) -> "o":
        """Signal ConnectionRemoved."""
        return "/org/freedesktop/NetworkManager/Settings/1"

    @dbus_method()
    def ListConnections(self) -> "ao":
        """Do ListConnections method."""
        return self.Connections()

    @dbus_method()
    def GetConnectionByUuid(self, uuid: "s") -> "o":
        """Do GetConnectionByUuid method."""
        return "/org/freedesktop/NetworkManager/Settings/1"

    @dbus_method()
    def AddConnection(self, connection: "a{sa{sv}}") -> "o":
        """Do AddConnection method."""
        self.NewConnection()
        return "/org/freedesktop/NetworkManager/Settings/1"

    @dbus_method()
    def AddConnectionUnsaved(self, connection: "a{sa{sv}}") -> "o":
        """Do AddConnectionUnsaved method."""
        return "/org/freedesktop/NetworkManager/Settings/1"

    @dbus_method()
    def AddConnection2(
        self, settings: "a{sa{sv}}", flags: "u", args: "a{sv}"
    ) -> "oa{sv}":
        """Do AddConnection2 method."""
        self.NewConnection()
        return ["/org/freedesktop/NetworkManager/Settings/1", {}]

    @dbus_method()
    def LoadConnections(self, filenames: "as") -> "bas":
        """Do LoadConnections method."""
        self.NewConnection()
        return [True, []]

    @dbus_method()
    def ReloadConnections(self) -> "b":
        """Do ReloadConnections method."""
        return True

    @dbus_method()
    def SaveHostname(self, hostname: "s") -> None:
        """Do SaveHostname method."""
