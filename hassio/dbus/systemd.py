"""Interface to Systemd over dbus."""
import logging

from ..exceptions import HassioInternalError
from ..utils.gdbus import DBus, DBusError

_LOGGER = logging.getLogger(__name__)

DBUS_NAME = 'org.freedesktop.systemd1'
DBUS_OBJECT = '/org/freedesktop/systemd1'


class Systemd:
    """Systemd function handler."""

    def __init__(self):
        """Initialize systemd."""
        self.dbus = None

    @property
    def is_connected(self):
        """Return True, if they is connected to dbus."""
        return self.dbus is not None

    async def connect(self):
        """Connect do bus."""
        try:
            self.dbus = await DBus.connect(DBUS_NAME, DBUS_OBJECT)
        except DBusError:
            _LOGGER.warning("Can't connect to systemd")

    async def reboot(self):
        """Reboot host computer."""
        try:
            await self.dbus.Manager.Reboot()
        except DBusError:
            _LOGGER.error("Can't reboot host")
            raise HassioInternalError() from None

    async def shutdown(self):
        """Shutdown host computer."""
        try:
            await self.dbus.Manager.PowerOff()
        except DBusError:
            _LOGGER.error("Can't PowerOff host")
            raise HassioInternalError() from None
