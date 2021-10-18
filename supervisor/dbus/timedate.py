"""Interface to systemd-timedate over D-Bus."""
from datetime import datetime
import logging
from typing import Any

from ..exceptions import DBusError, DBusInterfaceError
from ..utils.dbus import DBus
from ..utils.dt import utc_from_timestamp
from .const import (
    DBUS_ATTR_LOCALRTC,
    DBUS_ATTR_NTP,
    DBUS_ATTR_NTPSYNCHRONIZED,
    DBUS_ATTR_TIMEUSEC,
    DBUS_ATTR_TIMEZONE,
    DBUS_NAME_TIMEDATE,
    DBUS_OBJECT_TIMEDATE,
)
from .interface import DBusInterface, dbus_property
from .utils import dbus_connected

_LOGGER: logging.Logger = logging.getLogger(__name__)


class TimeDate(DBusInterface):
    """Timedate function handler."""

    name = DBUS_NAME_TIMEDATE

    def __init__(self) -> None:
        """Initialize Properties."""
        self.properties: dict[str, Any] = {}

    @property
    @dbus_property
    def timezone(self) -> str:
        """Return host timezone."""
        return self.properties[DBUS_ATTR_TIMEZONE]

    @property
    @dbus_property
    def local_rtc(self) -> bool:
        """Return if a local RTC exists."""
        return self.properties[DBUS_ATTR_LOCALRTC]

    @property
    @dbus_property
    def ntp(self) -> bool:
        """Return if NTP is enabled."""
        return self.properties[DBUS_ATTR_NTP]

    @property
    @dbus_property
    def ntp_synchronized(self) -> bool:
        """Return if NTP is synchronized."""
        return self.properties[DBUS_ATTR_NTPSYNCHRONIZED]

    @property
    @dbus_property
    def dt_utc(self) -> datetime:
        """Return the system UTC time."""
        return utc_from_timestamp(self.properties[DBUS_ATTR_TIMEUSEC] / 1000000)

    async def connect(self):
        """Connect to D-Bus."""
        try:
            self.dbus = await DBus.connect(DBUS_NAME_TIMEDATE, DBUS_OBJECT_TIMEDATE)
        except DBusError:
            _LOGGER.warning("Can't connect to systemd-timedate")
        except DBusInterfaceError:
            _LOGGER.warning(
                "No timedate support on the host. Time/Date functions have been disabled."
            )

    @dbus_connected
    def set_time(self, utc: datetime):
        """Set time & date on host as UTC.

        Return a coroutine.
        """
        return self.dbus.SetTime(int(utc.timestamp() * 1000000), False, False)

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
