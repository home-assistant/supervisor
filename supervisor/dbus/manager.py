"""D-Bus interface objects."""
import logging

from ..const import SOCKET_DBUS
from ..coresys import CoreSys, CoreSysAttributes
from .agent import OSAgent
from .hostname import Hostname
from .interface import DBusInterface
from .logind import Logind
from .network import NetworkManager
from .rauc import Rauc
from .systemd import Systemd
from .timedate import TimeDate

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

    async def load(self) -> None:
        """Connect interfaces to D-Bus."""
        if not SOCKET_DBUS.exists():
            _LOGGER.error(
                "No D-Bus support on Host. Disabled any kind of host control!"
            )
            return

        dbus_loads: list[DBusInterface] = [
            self.agent,
            self.systemd,
            self.logind,
            self.hostname,
            self.timedate,
            self.network,
            self.rauc,
        ]
        for dbus in dbus_loads:
            _LOGGER.info("Load dbus interface %s", dbus.name)
            try:
                await dbus.connect()
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.warning("Can't load dbus interface %s: %s", dbus.name, err)

        self.sys_host.supported_features.cache_clear()
