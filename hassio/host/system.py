"""Interface to Systemd over dbus."""


from ..utils.gdbus import DBus, DBusError

DBUS_NAME = 'org.freedesktop.systemd1'
DBUS_OBJECT = '/org/freedesktop/systemd1/Manager'


class System(object):
    """Systemd function handler."""

    def __init__(self):
        """Initialize systemd."""
        self.dbus = None

    async def load(self):
        """Connect do bus."""
        try:
            self.dbus = await DBus.connect(DBUS_NAME, DBUS_OBJECT)
        except DBusError:
            return

    async def reboot():
        """Reboot host computer."""
        try:
            await self.dbus.Reboot()
        except DBusError:
            _LOGGER.error("Can't reboot host")

    async def shutdown():
        """Shutdown host computer."""
