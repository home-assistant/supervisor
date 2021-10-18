"""AppArmor object for OS-Agent."""
from pathlib import Path
from typing import Any

from awesomeversion import AwesomeVersion

from ...utils.dbus import DBus
from ..const import (
    DBUS_ATTR_PARSER_VERSION,
    DBUS_NAME_HAOS,
    DBUS_NAME_HAOS_APPARMOR,
    DBUS_OBJECT_HAOS_APPARMOR,
)
from ..interface import DBusInterface, dbus_property
from ..utils import dbus_connected


class AppArmor(DBusInterface):
    """AppArmor object for OS Agent."""

    def __init__(self) -> None:
        """Initialize Properties."""
        self.properties: dict[str, Any] = {}

    @property
    @dbus_property
    def version(self) -> AwesomeVersion:
        """Return version of host AppArmor parser."""
        return AwesomeVersion(self.properties[DBUS_ATTR_PARSER_VERSION])

    async def connect(self) -> None:
        """Get connection information."""
        self.dbus = await DBus.connect(DBUS_NAME_HAOS, DBUS_OBJECT_HAOS_APPARMOR)

    @dbus_connected
    async def update(self):
        """Update Properties."""
        self.properties = await self.dbus.get_properties(DBUS_NAME_HAOS_APPARMOR)

    @dbus_connected
    async def load_profile(self, profile: Path, cache: Path) -> None:
        """Load/Update AppArmor profile."""
        await self.dbus.AppArmor.LoadProfile(profile.as_posix(), cache.as_posix())

    @dbus_connected
    async def unload_profile(self, profile: Path, cache: Path) -> None:
        """Remove AppArmor profile."""
        await self.dbus.AppArmor.UnloadProfile(profile.as_posix(), cache.as_posix())
