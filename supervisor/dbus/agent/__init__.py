"""OS-Agent implementation for DBUS."""

import asyncio
from collections.abc import Awaitable
import logging
from typing import Any

from awesomeversion import AwesomeVersion
from dbus_fast.aio.message_bus import MessageBus

from ...exceptions import DBusInterfaceError, DBusServiceUnkownError
from ..const import (
    DBUS_ATTR_DIAGNOSTICS,
    DBUS_ATTR_VERSION,
    DBUS_IFACE_HAOS,
    DBUS_NAME_HAOS,
    DBUS_OBJECT_HAOS,
)
from ..interface import DBusInterface, DBusInterfaceProxy, dbus_property
from ..utils import dbus_connected
from .apparmor import AppArmor
from .boards import BoardManager
from .cgroup import CGroup
from .datadisk import DataDisk
from .swap import Swap
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
        super().__init__()

        self._apparmor: AppArmor = AppArmor()
        self._board: BoardManager = BoardManager()
        self._cgroup: CGroup = CGroup()
        self._datadisk: DataDisk = DataDisk()
        self._swap: Swap = Swap()
        self._system: System = System()

    @property
    def cgroup(self) -> CGroup:
        """Return CGroup DBUS object."""
        return self._cgroup

    @property
    def apparmor(self) -> AppArmor:
        """Return AppArmor DBUS object."""
        return self._apparmor

    @property
    def swap(self) -> Swap:
        """Return Swap DBUS object."""
        return self._swap

    @property
    def system(self) -> System:
        """Return System DBUS object."""
        return self._system

    @property
    def datadisk(self) -> DataDisk:
        """Return DataDisk DBUS object."""
        return self._datadisk

    @property
    def board(self) -> BoardManager:
        """Return board manager."""
        return self._board

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

    @dbus_connected
    def set_diagnostics(self, value: bool) -> Awaitable[None]:
        """Enable or disable OS-Agent diagnostics."""
        return self.connected_dbus.set("diagnostics", value)

    @property
    def all(self) -> list[DBusInterface]:
        """Return all managed dbus interfaces."""
        return [
            self.apparmor,
            self.board,
            self.cgroup,
            self.datadisk,
            self.swap,
            self.system,
        ]

    async def connect(self, bus: MessageBus) -> None:
        """Connect to system's D-Bus."""
        _LOGGER.info("Load dbus interface %s", self.name)
        try:
            await super().connect(bus)
        except (DBusServiceUnkownError, DBusInterfaceError):
            _LOGGER.error(
                "No OS-Agent support on the host. Some Host functions have been disabled."
            )
            return

        errors = await asyncio.gather(
            *[dbus.connect(bus) for dbus in self.all], return_exceptions=True
        )

        for err in errors:
            if err:
                dbus = self.all[errors.index(err)]
                _LOGGER.error(
                    "Can't load OS Agent dbus interface %s %s: %s",
                    dbus.bus_name,
                    dbus.object_path,
                    err,
                )

    @dbus_connected
    async def update(self, changed: dict[str, Any] | None = None) -> None:
        """Update Properties."""
        await super().update(changed)

        if not changed:
            await asyncio.gather(
                *[
                    dbus.update()
                    for dbus in [self.apparmor, self.board, self.datadisk]
                    if dbus.is_connected
                ]
            )

    def shutdown(self) -> None:
        """Shutdown the object and disconnect from D-Bus.

        This method is irreversible.
        """
        for dbus in self.all:
            dbus.shutdown()

        super().shutdown()
