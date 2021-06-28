"""Network Manager implementation for DBUS."""
import asyncio
import logging
from typing import Any, Dict

from awesomeversion import AwesomeVersion

from ...exceptions import DBusError, DBusInterfaceError
from ...utils.gdbus import DBus
from ..const import (
    DBUS_ATTR_DIAGNOSTICS,
    DBUS_ATTR_VERSION,
    DBUS_NAME_HAOS,
    DBUS_OBJECT_HAOS,
)
from ..interface import DBusInterface, dbus_property
from ..utils import dbus_connected

_LOGGER: logging.Logger = logging.getLogger(__name__)


class OSAgent(DBusInterface):
    """Handle D-Bus interface for OS-Agent."""

    name = DBUS_NAME_HAOS

    def __init__(self) -> None:
        """Initialize Properties."""
        self.properties: Dict[str, Any] = {}

    @property
    @dbus_property
    def version(self) -> AwesomeVersion:
        """Return version of OS-Agent."""
        return AwesomeVersion(self.properties[DBUS_ATTR_VERSION])

    @property
    @dbus_property
    def diagnostics(self) -> bool:
        """Return if diagnostics is enabled on OS-Agent."""
        return self.properties[DBUS_ATTR_DIAGNOSTICS]

    @diagnostics.setter
    def diagnostics(self, value: bool) -> None:
        """Enable oder disable OS-Agent diagnostics."""
        asyncio.create_task(
            self.dbus.set_property(DBUS_NAME_HAOS, DBUS_ATTR_DIAGNOSTICS, value)
        )

    async def connect(self) -> None:
        """Connect to system's D-Bus."""
        try:
            self.dbus = await DBus.connect(DBUS_NAME_HAOS, DBUS_OBJECT_HAOS)
        except DBusError:
            _LOGGER.warning("Can't connect to OS-Agent")
        except DBusInterfaceError:
            _LOGGER.warning(
                "No OS-Agent support on the host. Some Host functions have been disabled."
            )

    @dbus_connected
    async def update(self):
        """Update Properties."""
        self.properties = await self.dbus.get_properties(DBUS_NAME_HAOS)
