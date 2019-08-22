"""Interface class for D-Bus wrappers."""
from typing import Optional

from ..utils.gdbus import DBus


class DBusInterface:
    """Handle D-Bus interface for hostname/system."""

    dbus: Optional[DBus] = None

    @property
    def is_connected(self):
        """Return True, if they is connected to D-Bus."""
        return self.dbus is not None

    async def connect(self):
        """Connect to D-Bus."""
        raise NotImplementedError()
