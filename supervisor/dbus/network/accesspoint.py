"""Connection object for Network Manager."""

from ..const import (
    DBUS_ATTR_FREQUENCY,
    DBUS_ATTR_HWADDRESS,
    DBUS_ATTR_MODE,
    DBUS_ATTR_SSID,
    DBUS_ATTR_STRENGTH,
    DBUS_IFACE_ACCESSPOINT,
    DBUS_NAME_NM,
)
from ..interface import DBusInterfaceProxy, dbus_property


class NetworkWirelessAP(DBusInterfaceProxy):
    """NetworkWireless AP object for Network Manager.

    https://developer.gnome.org/NetworkManager/stable/gdbus-org.freedesktop.NetworkManager.AccessPoint.html
    """

    bus_name: str = DBUS_NAME_NM
    properties_interface: str = DBUS_IFACE_ACCESSPOINT
    # Don't sync these. They may disappear and strength changes a lot
    sync_properties: bool = False

    def __init__(self, object_path: str) -> None:
        """Initialize NetworkWireless AP object."""
        self._object_path: str = object_path
        super().__init__()

    @property
    def object_path(self) -> str:
        """Object path for dbus object."""
        return self._object_path

    @property
    @dbus_property
    def ssid(self) -> str:
        """Return details about ssid."""
        return bytes(self.properties[DBUS_ATTR_SSID]).decode()

    @property
    @dbus_property
    def frequency(self) -> int:
        """Return details about frequency."""
        return self.properties[DBUS_ATTR_FREQUENCY]

    @property
    @dbus_property
    def mac(self) -> str:
        """Return details about mac address."""
        return self.properties[DBUS_ATTR_HWADDRESS]

    @property
    @dbus_property
    def mode(self) -> int:
        """Return details about mode."""
        return self.properties[DBUS_ATTR_MODE]

    @property
    @dbus_property
    def strength(self) -> int:
        """Return details about strength."""
        return int(self.properties[DBUS_ATTR_STRENGTH])
