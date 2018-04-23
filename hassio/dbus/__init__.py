"""DBus interface objects."""

from .systemd import Systemd
from ..coresys import CoreSysAttributes


class DBusManager(CoreSysAttributes):
    """DBus Interface handler."""

    def __init__(self, coresys):
        """Initialize DBus  Interface."""
        self.coresys = coresys
        self._systemd = Systemd()

    @property
    def systemd(self):
        """Return Systemd Interface."""
        return self._systemd

    async def load(self):
        """Connect interfaces to dbus."""
        await self.systemd.connect()
