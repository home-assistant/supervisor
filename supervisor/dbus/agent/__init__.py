"""OS-Agent implementation for DBUS."""
import asyncio
import logging
from typing import Any

from awesomeversion import AwesomeVersion

from ...exceptions import DBusError, DBusInterfaceError
from ...utils.dbus import DBus
from ..const import (
    DBUS_ATTR_DIAGNOSTICS,
    DBUS_ATTR_VERSION,
    DBUS_IFACE_HAOS,
    DBUS_NAME_HAOS,
    DBUS_OBJECT_HAOS,
)
from ..interface import DBusInterface, dbus_property
from ..utils import dbus_connected
from .apparmor import AppArmor
from .cgroup import CGroup
from .datadisk import DataDisk
from .system import System

_LOGGER: logging.Logger = logging.getLogger(__name__)


class OSAgent(DBusInterface):
    """Handle D-Bus interface for OS-Agent."""

    name = DBUS_NAME_HAOS

    def __init__(self) -> None:
        """Initialize Properties."""
        self.properties: dict[str, Any] = {}

        self._cgroup: CGroup = CGroup()
        self._apparmor: AppArmor = AppArmor()
        self._system: System = System()
        self._datadisk: DataDisk = DataDisk()

    @property
    def cgroup(self) -> CGroup:
        """Return CGroup DBUS object."""
        return self._cgroup

    @property
    def apparmor(self) -> AppArmor:
        """Return AppArmor DBUS object."""
        return self._apparmor

    @property
    def system(self) -> System:
        """Return System DBUS object."""
        return self._system

    @property
    def datadisk(self) -> DataDisk:
        """Return DataDisk DBUS object."""
        return self._datadisk

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
    @dbus_property
    def diagnostics(self, value: bool) -> None:
        """Enable or disable OS-Agent diagnostics."""
        asyncio.create_task(
            self.dbus.set_property(DBUS_IFACE_HAOS, DBUS_ATTR_DIAGNOSTICS, value)
        )

    async def connect(self) -> None:
        """Connect to system's D-Bus."""
        try:
            self.dbus = await DBus.connect(DBUS_NAME_HAOS, DBUS_OBJECT_HAOS)
            await self.cgroup.connect()
            await self.apparmor.connect()
            await self.system.connect()
            await self.datadisk.connect()
        except DBusError:
            _LOGGER.warning("Can't connect to OS-Agent")
        except DBusInterfaceError:
            _LOGGER.warning(
                "No OS-Agent support on the host. Some Host functions have been disabled."
            )

    @dbus_connected
    async def update(self):
        """Update Properties."""
        self.properties = await self.dbus.get_properties(DBUS_IFACE_HAOS)
        await self.apparmor.update()
        await self.datadisk.update()
