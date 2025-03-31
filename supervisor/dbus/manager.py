"""D-Bus interface objects."""

import asyncio
import logging

from dbus_fast import BusType
from dbus_fast.aio.message_bus import MessageBus

from ..const import SOCKET_DBUS
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import DBusFatalError
from .agent import OSAgent
from .hostname import Hostname
from .interface import DBusInterface
from .logind import Logind
from .network import NetworkManager
from .rauc import Rauc
from .resolved import Resolved
from .systemd import Systemd
from .timedate import TimeDate
from .udisks2 import UDisks2Manager

_LOGGER: logging.Logger = logging.getLogger(__name__)


class DBusManager(CoreSysAttributes):
    """A DBus Interface handler."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize D-Bus interface."""
        self.coresys: CoreSys = coresys

        self._systemd: Systemd = Systemd()
        self._logind: Logind = Logind()
        self._hostname: Hostname = Hostname()
        self._rauc: Rauc = Rauc()
        self._network: NetworkManager = NetworkManager()
        self._agent: OSAgent = OSAgent()
        self._timedate: TimeDate = TimeDate()
        self._resolved: Resolved = Resolved()
        self._udisks2: UDisks2Manager = UDisks2Manager()
        self._bus: MessageBus | None = None

    @property
    def systemd(self) -> Systemd:
        """Return the systemd interface."""
        return self._systemd

    @property
    def logind(self) -> Logind:
        """Return the logind interface."""
        return self._logind

    @property
    def hostname(self) -> Hostname:
        """Return the hostname interface."""
        return self._hostname

    @property
    def rauc(self) -> Rauc:
        """Return the rauc interface."""
        return self._rauc

    @property
    def network(self) -> NetworkManager:
        """Return NetworkManager interface."""
        return self._network

    @property
    def agent(self) -> OSAgent:
        """Return OS-Agent interface."""
        return self._agent

    @property
    def timedate(self) -> TimeDate:
        """Return the timedate interface."""
        return self._timedate

    @property
    def resolved(self) -> Resolved:
        """Return the resolved interface."""
        return self._resolved

    @property
    def udisks2(self) -> UDisks2Manager:
        """Return the udisks2 interface."""
        return self._udisks2

    @property
    def bus(self) -> MessageBus | None:
        """Return the message bus."""
        return self._bus

    @property
    def all(self) -> list[DBusInterface]:
        """Return all managed dbus interfaces."""
        return [
            self.agent,
            self.hostname,
            self.logind,
            self.network,
            self.rauc,
            self.resolved,
            self.systemd,
            self.timedate,
            self.udisks2,
        ]

    async def load(self) -> None:
        """Connect interfaces to D-Bus."""
        if not SOCKET_DBUS.exists():
            _LOGGER.error(
                "No D-Bus support on Host. Disabled any kind of host control!"
            )
            return

        try:
            self._bus = connected_bus = await MessageBus(
                bus_type=BusType.SYSTEM
            ).connect()
        except Exception as err:
            raise DBusFatalError(
                "Cannot connect to system D-Bus. Disabled any kind of host control!"
            ) from err

        _LOGGER.info("Connected to system D-Bus.")

        errors = await asyncio.gather(
            *[dbus.connect(connected_bus) for dbus in self.all], return_exceptions=True
        )

        for error in errors:
            if error:
                dbus = self.all[errors.index(error)]
                _LOGGER.warning(
                    "Can't load dbus interface %s %s: %s",
                    dbus.name,
                    dbus.object_path,
                    error,
                )

        self.sys_host.supported_features.cache_clear()

    async def unload(self) -> None:
        """Close connection to D-Bus."""
        if not self.bus:
            _LOGGER.warning("No D-Bus connection to close.")
            return

        for dbus in self.all:
            dbus.shutdown()

        self.bus.disconnect()
        _LOGGER.info("Closed conection to system D-Bus.")
