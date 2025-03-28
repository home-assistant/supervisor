"""Board dbus proxy interface."""

from voluptuous import Schema

from ....const import FILE_HASSIO_BOARD
from ....utils.common import FileConfiguration
from ...const import DBUS_IFACE_HAOS_BOARDS, DBUS_NAME_HAOS, DBUS_OBJECT_HAOS_BOARDS
from ...interface import DBusInterfaceProxy
from .validate import SCHEMA_BASE_BOARD


class BoardProxy(FileConfiguration, DBusInterfaceProxy):
    """DBus interface proxy for os board."""

    bus_name: str = DBUS_NAME_HAOS

    def __init__(self, name: str, file_schema: Schema | None = None) -> None:
        """Initialize properties."""
        self._name: str = name
        self._object_path: str = f"{DBUS_OBJECT_HAOS_BOARDS}/{name}"
        self._properties_interface: str = f"{DBUS_IFACE_HAOS_BOARDS}.{name}"
        super().__init__(FILE_HASSIO_BOARD, file_schema or SCHEMA_BASE_BOARD)
        super(FileConfiguration, self).__init__()

    @property
    def object_path(self) -> str:
        """Object path for dbus object."""
        return self._object_path

    @property
    def properties_interface(self) -> str:
        """Primary interface of object to get property values from."""
        return self._properties_interface

    @property
    def name(self) -> str:
        """Get name."""
        return self._name
