"""D-Bus interface objects."""
import logging

from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import DBusNotConnectedError
from ..network import NetworkManager
from .hostname import Hostname
from .nmi_dns import NMIDnsManager
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
        self._nmi_dns: NMIDnsManager = NMIDnsManager()
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
    def nmi_dns(self) -> NMIDnsManager:
        """Return NetworkManager DNS interface."""
        return self._nmi_dns

    @property
    def network(self) -> NetworkManager:
        """Return NetworkManager interface."""
        return self._network

    async def load(self) -> None:
        """Connect interfaces to D-Bus."""

        try:
            await self.systemd.connect()
            await self.hostname.connect()
            await self.rauc.connect()
            await self.nmi_dns.connect()
            await self.network.connect()
        except DBusNotConnectedError:
            _LOGGER.error(
                "No DBus support from Host. Disabled any kind of host control!"
            )
