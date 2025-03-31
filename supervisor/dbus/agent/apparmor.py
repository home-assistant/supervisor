"""AppArmor object for OS-Agent."""

from pathlib import Path

from awesomeversion import AwesomeVersion

from ..const import (
    DBUS_ATTR_PARSER_VERSION,
    DBUS_IFACE_HAOS_APPARMOR,
    DBUS_NAME_HAOS,
    DBUS_OBJECT_HAOS_APPARMOR,
)
from ..interface import DBusInterfaceProxy, dbus_property
from ..utils import dbus_connected


class AppArmor(DBusInterfaceProxy):
    """AppArmor object for OS Agent."""

    bus_name: str = DBUS_NAME_HAOS
    object_path: str = DBUS_OBJECT_HAOS_APPARMOR
    properties_interface: str = DBUS_IFACE_HAOS_APPARMOR

    @property
    @dbus_property
    def version(self) -> AwesomeVersion:
        """Return version of host AppArmor parser."""
        return AwesomeVersion(self.properties[DBUS_ATTR_PARSER_VERSION])

    @dbus_connected
    async def load_profile(self, profile: Path, cache: Path) -> None:
        """Load/Update AppArmor profile."""
        await self.connected_dbus.AppArmor.call(
            "load_profile", profile.as_posix(), cache.as_posix()
        )

    @dbus_connected
    async def unload_profile(self, profile: Path, cache: Path) -> None:
        """Remove AppArmor profile."""
        await self.connected_dbus.AppArmor.call(
            "unload_profile", profile.as_posix(), cache.as_posix()
        )
