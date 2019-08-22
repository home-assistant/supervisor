"""D-Bus interface objects."""
import logging

from .systemd import Systemd
from .hostname import Hostname
from .rauc import Rauc
from ..coresys import CoreSysAttributes, CoreSys
from ..exceptions import DBusNotConnectedError

_LOGGER: logging.Logger = logging.getLogger(__name__)


class DBusManager(CoreSysAttributes):
    """A DBus Interface handler."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize D-Bus interface."""
        self.coresys: CoreSys = coresys

        self._systemd: Systemd = Systemd()
        self._hostname: Hostname = Hostname()
        self._rauc: Rauc = Rauc()

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

    async def load(self) -> None:
        """Connect interfaces to D-Bus."""

        try:
            await self.systemd.connect()
            await self.hostname.connect()
            await self.rauc.connect()
        except DBusNotConnectedError:
            _LOGGER.error(
                "No DBus support from Host. Disable any kind of Host control!"
            )
