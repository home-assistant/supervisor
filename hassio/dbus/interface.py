"""Interface class for dbus wrappers."""


class DBusInterface:
    """Handle DBus interface for hostname/system."""

    def __init__(self):
        """Initialize systemd."""
        self.dbus = None

    @property
    def is_connected(self):
        """Return True, if they is connected to dbus."""
        return self.dbus is not None

    async def connect(self):
        """Connect do bus."""
        raise NotImplementedError()
