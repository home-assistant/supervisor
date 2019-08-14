"""D-Bus interface objects."""

from .systemd import Systemd
from .hostname import Hostname
from .rauc import Rauc
from ..coresys import CoreSysAttributes


class DBusManager(CoreSysAttributes):
    """A DBus Interface handler."""

    def __init__(self, coresys):
        """Initialize D-Bus interface."""
        self.coresys = coresys

        self._systemd = Systemd()
        self._hostname = Hostname()
        self._rauc = Rauc(coresys)

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
        await self.systemd.connect()
        await self.hostname.connect()
        await self.rauc.connect()
