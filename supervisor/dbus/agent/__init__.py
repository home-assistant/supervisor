"""OS-Agent implementation for DBUS."""
import asyncio
import logging
from typing import Any

from awesomeversion import AwesomeVersion
from dbus_fast.aio.message_bus import MessageBus

from ...exceptions import DBusError, DBusInterfaceError
from ..const import (
    DBUS_ATTR_DIAGNOSTICS,
    DBUS_ATTR_VERSION,
    DBUS_IFACE_HAOS,
    DBUS_NAME_HAOS,
    DBUS_OBJECT_HAOS,
)
from ..interface import DBusInterfaceProxy, dbus_property
from ..utils import dbus_connected
from .apparmor import AppArmor
from .cgroup import CGroup
from .datadisk import DataDisk
from .system import System

_LOGGER: logging.Logger = logging.getLogger(__name__)


class OSAgent(DBusInterfaceProxy):
    """Handle D-Bus interface for OS-Agent."""

    name: str = DBUS_NAME_HAOS
    bus_name: str = DBUS_NAME_HAOS
    object_path: str = DBUS_OBJECT_HAOS
    properties_interface: str = DBUS_IFACE_HAOS

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
        asyncio.create_task(self.dbus.set_diagnostics(value))

    async def connect(self, bus: MessageBus) -> None:
        """Connect to system's D-Bus."""
        _LOGGER.info("Load dbus interface %s", self.name)
        try:
            await super().connect(bus)
            await self.cgroup.connect(bus)
            await self.apparmor.connect(bus)
            await self.system.connect(bus)
            await self.datadisk.connect(bus)
        except DBusError:
            _LOGGER.warning("Can't connect to OS-Agent")
        except DBusInterfaceError:
            _LOGGER.warning(
                "No OS-Agent support on the host. Some Host functions have been disabled."
            )

    @dbus_connected
    async def update(self, changed: dict[str, Any] | None = None) -> None:
        """Update Properties."""
        await super().update(changed)

        if not changed and self.apparmor.is_connected:
            await self.apparmor.update()

        if not changed and self.datadisk.is_connected:
            await self.datadisk.update()

    def disconnect(self) -> None:
        """Disconnect from D-Bus."""
        self.cgroup.disconnect()
        self.apparmor.disconnect()
        self.system.disconnect()
        self.datadisk.disconnect()
        super().disconnect()
