"""Interface to Logind over D-Bus."""
import logging
from typing import Any, Dict

from ..exceptions import DBusError, DBusInterfaceError
from ..utils.gdbus import DBus
from .const import (
    DBUS_ATTR_LOCALRTC,
    DBUS_ATTR_NTP,
    DBUS_ATTR_TIMEZONE,
    DBUS_NAME_TIMEDATE,
    DBUS_OBJECT_TIMEDATE,
)
from .interface import DBusInterface
from .utils import dbus_connected

_LOGGER: logging.Logger = logging.getLogger(__name__)


class TimeDate(DBusInterface):
    """Timedate function handler."""

    name = DBUS_NAME_TIMEDATE

    def __init__(self) -> None:
        """Initialize Properties."""
        self.properties: Dict[str, Any] = {}

    @property
    def timezone(self) -> str:
        """Return host timezone."""
        return self.properties[DBUS_ATTR_TIMEZONE]

    @property
    def local_rtc(self) -> bool:
        """Return if a local RTC exists."""
        return self.properties[DBUS_ATTR_LOCALRTC]

    @property
    def ntp(self) -> bool:
        """Return if NTP is enabled."""
        return self.properties[DBUS_ATTR_NTP]

    async def connect(self):
        """Connect to D-Bus."""
        try:
            self.dbus = await DBus.connect(DBUS_NAME_TIMEDATE, DBUS_OBJECT_TIMEDATE)
        except DBusError:
            _LOGGER.warning("Can't connect to systemd-timedate")
        except DBusInterfaceError:
            _LOGGER.info("No systemd-timedate support on the host.")

    @dbus_connected
    def set_time(self, usec_utc: int, relative: bool):
        """Set time & date on host as UTC.

        Return a coroutine.
        """
        return self.dbus.SetTime(usec_utc, relative, False)

    @dbus_connected
    def set_ntp(self, use_ntp: bool):
        """Turn NTP on or off.

        Return a coroutine.
        """
        return self.dbus.SetNTP(use_ntp)

    @dbus_connected
    async def update(self):
        """Update Properties."""
        self.properties = await self.dbus.get_properties(DBUS_NAME_TIMEDATE)
