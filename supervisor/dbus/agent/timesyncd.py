"""Timesyncd configuration object for OS Agent."""

from collections.abc import Awaitable

from ..const import (
    DBUS_ATTR_FALLBACK_NTP_SERVER,
    DBUS_ATTR_NTP_SERVER,
    DBUS_IFACE_HAOS_CONFIG_TIMESYNCD,
    DBUS_NAME_HAOS,
    DBUS_OBJECT_HAOS_CONFIG_TIMESYNCD,
)
from ..interface import DBusInterfaceProxy, dbus_property


class Timesyncd(DBusInterfaceProxy):
    """Timesyncd object for OS Agent."""

    bus_name: str = DBUS_NAME_HAOS
    object_path: str = DBUS_OBJECT_HAOS_CONFIG_TIMESYNCD
    properties_interface: str = DBUS_IFACE_HAOS_CONFIG_TIMESYNCD

    @property
    @dbus_property
    def ntp_servers(self) -> list[str]:
        """Get NTP servers."""
        return self.properties[DBUS_ATTR_NTP_SERVER]

    def set_ntp_servers(self, servers: list[str]) -> Awaitable[None]:
        """Set NTP servers."""
        return self.connected_dbus.Config.Timesyncd.set("ntp_server", servers)

    @property
    @dbus_property
    def fallback_ntp_servers(self) -> list[str]:
        """Get fallback NTP servers."""
        return self.properties[DBUS_ATTR_FALLBACK_NTP_SERVER]

    def set_fallback_ntp_servers(self, servers: list[str]) -> Awaitable[None]:
        """Set fallback NTP servers."""
        return self.connected_dbus.Config.Timesyncd.set("fallback_ntp_server", servers)
