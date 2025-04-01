"""Interface to systemd-timedate over D-Bus."""

import asyncio
from datetime import datetime, tzinfo
import logging
from typing import Any

from dbus_fast.aio.message_bus import MessageBus

from ..exceptions import DBusError, DBusInterfaceError, DBusServiceUnkownError
from ..utils.dt import get_time_zone, utc_from_timestamp
from .const import (
    DBUS_ATTR_NTP,
    DBUS_ATTR_NTPSYNCHRONIZED,
    DBUS_ATTR_TIMEUSEC,
    DBUS_ATTR_TIMEZONE,
    DBUS_IFACE_TIMEDATE,
    DBUS_NAME_TIMEDATE,
    DBUS_OBJECT_TIMEDATE,
)
from .interface import DBusInterfaceProxy, dbus_property
from .utils import dbus_connected

_LOGGER: logging.Logger = logging.getLogger(__name__)


class TimeDate(DBusInterfaceProxy):
    """Timedate function handler.

    https://www.freedesktop.org/software/systemd/man/org.freedesktop.timedate1.html
    """

    name: str = DBUS_NAME_TIMEDATE
    bus_name: str = DBUS_NAME_TIMEDATE
    object_path: str = DBUS_OBJECT_TIMEDATE
    properties_interface: str = DBUS_IFACE_TIMEDATE

    def __init__(self) -> None:
        """Initialize object."""
        super().__init__()
        self._timezone_tzinfo: tzinfo | None = None

    @property
    @dbus_property
    def timezone(self) -> str:
        """Return host timezone."""
        return self.properties[DBUS_ATTR_TIMEZONE]

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

    @property
    def timezone_tzinfo(self) -> tzinfo | None:
        """Return timezone as tzinfo object."""
        return self._timezone_tzinfo

    async def connect(self, bus: MessageBus):
        """Connect to D-Bus."""
        _LOGGER.info("Load dbus interface %s", self.name)
        try:
            await super().connect(bus)
        except DBusError:
            _LOGGER.warning("Can't connect to systemd-timedate")
        except (DBusServiceUnkownError, DBusInterfaceError):
            _LOGGER.warning(
                "No timedate support on the host. Time/Date functions have been disabled."
            )

    @dbus_connected
    async def update(self, changed: dict[str, Any] | None = None) -> None:
        """Update properties via D-Bus."""
        timezone = self.timezone
        await super().update(changed)

        if not self.timezone:
            self._timezone_tzinfo = None
        elif timezone != self.timezone:
            self._timezone_tzinfo = await asyncio.get_running_loop().run_in_executor(
                None, get_time_zone, self.timezone
            )

    @dbus_connected
    async def set_time(self, utc: datetime) -> None:
        """Set time & date on host as UTC."""
        await self.connected_dbus.call(
            "set_time", int(utc.timestamp() * 1000000), False, False
        )

    @dbus_connected
    async def set_ntp(self, use_ntp: bool) -> None:
        """Turn NTP on or off."""
        await self.connected_dbus.call("set_ntp", use_ntp, False)
