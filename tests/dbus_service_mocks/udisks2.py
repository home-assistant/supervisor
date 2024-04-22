"""Mock of base UDisks2 service."""

from dbus_fast import Variant
from dbus_fast.service import signal

from .base import DBusServiceMock, dbus_method

BUS_NAME = "org.freedesktop.UDisks2"


def setup(object_path: str | None = None) -> DBusServiceMock:
    """Create dbus mock object."""
    return UDisks2()


class UDisks2(DBusServiceMock):
    """UDisks2 base object mock.

    gdbus introspect --system --dest org.freedesktop.UDisks2 --object-path /org/freedesktop/UDisks2
    """

    interface = "org.freedesktop.DBus.ObjectManager"
    object_path = "/org/freedesktop/UDisks2"
    response_get_managed_objects: dict[str, dict[str, dict[str, Variant]]] = {}

    @dbus_method()
    def GetManagedObjects(self) -> "a{oa{sa{sv}}}":
        """Do GetManagedObjects method."""
        return self.response_get_managed_objects

    @signal()
    def InterfacesAdded(
        self, object_path: str, interfaces_and_properties: dict[str, dict[str, Variant]]
    ) -> "oa{sa{sv}}":
        """Signal interfaces added."""
        return [object_path, interfaces_and_properties]

    @signal()
    def InterfacesRemoved(self, object_path: str, interfaces: list[str]) -> "oas":
        """Signal interfaces removed."""
        return [object_path, interfaces]
