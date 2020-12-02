"""D-Bus interface objects."""
import logging
from typing import List

from ..const import SOCKET_DBUS
from ..coresys import CoreSys, CoreSysAttributes
from .hostname import Hostname
from .interface import DBusInterface
from .network import NetworkManager
from .rauc import Rauc
from .systemd import Systemd

_LOGGER: logging.Logger = logging.getLogger(__name__)


class DBusManager(CoreSysAttributes):
    """A DBus Interface handler."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize D-Bus interface."""
        self.coresys: CoreSys = coresys

        self._systemd: Systemd = Systemd()
        self._hostname: Hostname = Hostname()
        self._rauc: Rauc = Rauc()
        self._network: NetworkManager = NetworkManager()

    @property
    def systemd(self) -> Systemd:
        """Return the systemd interface."""
        return self._systemd

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

    async def load(self) -> None:
        """Connect interfaces to D-Bus."""
        if not SOCKET_DBUS.exists():
            _LOGGER.error(
                "No D-Bus support on Host. Disabled any kind of host control!"
            )
            return

        dbus_loads: List[DBusInterface] = [
            self.systemd,
            self.hostname,
            self.rauc,
            self.network,
        ]
        for dbus in dbus_loads:
            try:
                await dbus.connect()
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.warning("Can't load dbus interface %s: %s", dbus.name, err)

        self.sys_host.supported_features.cache_clear()
