"""Interface class for D-Bus wrappers."""


class DBusInterface:
    """Handle D-Bus interface for hostname/system."""

    def __init__(self):
        """Initialize systemd."""
        self.dbus = None

    @property
    def is_connected(self):
        """Return True, if they is connected to D-Bus."""
        return self.dbus is not None

    async def connect(self):
        """Connect to D-Bus."""
        raise NotImplementedError()
