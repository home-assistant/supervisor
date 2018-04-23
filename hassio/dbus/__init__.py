"""DBus interface objects."""

from .systemd import Systemd
from .hostname import Hostname
from ..coresys import CoreSysAttributes


class DBusManager(CoreSysAttributes):
    """DBus Interface handler."""

    def __init__(self, coresys):
        """Initialize DBus  Interface."""
        self.coresys = coresys
        self._systemd = Systemd()
        self._hostname = Hostname()

    @property
    def systemd(self):
        """Return Systemd Interface."""
        return self._systemd

    @property
    def hostname(self):
        """Return hostname Interface."""
        return self._hostname

    async def load(self):
        """Connect interfaces to dbus."""
        await self.systemd.connect()
        await self.hostname.connect()
