"""Interface to Logind over D-Bus."""
import logging

from dbus_next.aio.message_bus import MessageBus

from ..exceptions import DBusError, DBusInterfaceError
from ..utils.dbus import DBus
from .const import DBUS_NAME_LOGIND, DBUS_OBJECT_LOGIND
from .interface import DBusInterface
from .utils import dbus_connected

_LOGGER: logging.Logger = logging.getLogger(__name__)


class Logind(DBusInterface):
    """Logind function handler.

    https://www.freedesktop.org/software/systemd/man/org.freedesktop.login1.html
    """

    name = DBUS_NAME_LOGIND

    async def connect(self, bus: MessageBus):
        """Connect to D-Bus."""
        try:
            self.dbus = await DBus.connect(bus, DBUS_NAME_LOGIND, DBUS_OBJECT_LOGIND)
        except DBusError:
            _LOGGER.warning("Can't connect to systemd-logind")
        except DBusInterfaceError:
            _LOGGER.info("No systemd-logind support on the host.")

    @dbus_connected
    async def reboot(self) -> None:
        """Reboot host computer."""
        await self.dbus.Manager.Reboot(False)

    @dbus_connected
    async def power_off(self) -> None:
        """Power off host computer."""
        await self.dbus.Manager.PowerOff(False)
