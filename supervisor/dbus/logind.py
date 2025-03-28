"""Interface to Logind over D-Bus."""

import logging

from dbus_fast.aio.message_bus import MessageBus

from ..exceptions import DBusError, DBusInterfaceError, DBusServiceUnkownError
from .const import DBUS_NAME_LOGIND, DBUS_OBJECT_LOGIND
from .interface import DBusInterface
from .utils import dbus_connected

_LOGGER: logging.Logger = logging.getLogger(__name__)


class Logind(DBusInterface):
    """Logind function handler.

    https://www.freedesktop.org/software/systemd/man/org.freedesktop.login1.html
    """

    name = DBUS_NAME_LOGIND
    bus_name: str = DBUS_NAME_LOGIND
    object_path: str = DBUS_OBJECT_LOGIND

    async def connect(self, bus: MessageBus):
        """Connect to D-Bus."""
        _LOGGER.info("Load dbus interface %s", self.name)
        try:
            await super().connect(bus)
        except DBusError:
            _LOGGER.warning("Can't connect to systemd-logind")
        except (DBusServiceUnkownError, DBusInterfaceError):
            _LOGGER.warning("No systemd-logind support on the host.")

    @dbus_connected
    async def reboot(self) -> None:
        """Reboot host computer."""
        await self.connected_dbus.Manager.call("reboot", False)

    @dbus_connected
    async def power_off(self) -> None:
        """Power off host computer."""
        await self.connected_dbus.Manager.call("power_off", False)
