"""D-Bus interface objects."""
import logging

from dbus_next.aio import MessageBus
from dbus_next import BusType

from .systemd import Systemd
from .hostname import Hostname
from .rauc import Rauc
from ..coresys import CoreSysAttributes, CoreSys

_LOGGER = logging.getLogger(__name__)


class DBusManager(CoreSysAttributes):
    """A DBus Interface handler."""

    def __init__(self, coresys: CoreSys):
        """Initialize D-Bus interface."""
        self.coresys: CoreSys = coresys

        self._dbus: MessageBus = MessageBus(bus_type=BusType.SYSTEM)

        self._systemd = Systemd(self._dbus)
        self._hostname = Hostname(self._dbus)
        self._rauc = Rauc(self._dbus)

    @property
    def systemd(self):
        """Return the systemd interface."""
        return self._systemd

    @property
    def hostname(self):
        """Return the hostname interface."""
        return self._hostname

    @property
    def rauc(self):
        """Return the rauc interface."""
        return self._rauc

    async def load(self):
        """Connect interfaces to D-Bus."""
        try:
            await self._dbus.connect()
        except OSError as err:
            _LOGGER.warning("Can't connect to DBUS: %s", err)
            return

        await self.systemd.connect()
        await self.hostname.connect()
        await self.rauc.connect()
