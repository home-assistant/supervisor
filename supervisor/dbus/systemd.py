"""Interface to Systemd over D-Bus."""
import logging
from typing import Any

from ..exceptions import DBusError, DBusInterfaceError
from ..utils.dbus import DBus
from .const import (
    DBUS_ATTR_FINISH_TIMESTAMP,
    DBUS_ATTR_FIRMWARE_TIMESTAMP_MONOTONIC,
    DBUS_ATTR_KERNEL_TIMESTAMP_MONOTONIC,
    DBUS_ATTR_LOADER_TIMESTAMP_MONOTONIC,
    DBUS_ATTR_USERSPACE_TIMESTAMP_MONOTONIC,
    DBUS_IFACE_SYSTEMD_MANAGER,
    DBUS_NAME_SYSTEMD,
    DBUS_OBJECT_SYSTEMD,
)
from .interface import DBusInterface, dbus_property
from .utils import dbus_connected

_LOGGER: logging.Logger = logging.getLogger(__name__)


class Systemd(DBusInterface):
    """Systemd function handler.

    https://www.freedesktop.org/software/systemd/man/org.freedesktop.systemd1.html
    """

    name = DBUS_NAME_SYSTEMD

    def __init__(self) -> None:
        """Initialize Properties."""
        self.properties: dict[str, Any] = {}

    async def connect(self):
        """Connect to D-Bus."""
        try:
            self.dbus = await DBus.connect(DBUS_NAME_SYSTEMD, DBUS_OBJECT_SYSTEMD)
        except DBusError:
            _LOGGER.warning("Can't connect to systemd")
        except DBusInterfaceError:
            _LOGGER.warning(
                "No systemd support on the host. Host control has been disabled."
            )

    @property
    @dbus_property
    def startup_time(self) -> float:
        """Return startup time in seconds."""
        return (
            float(self.properties[DBUS_ATTR_FIRMWARE_TIMESTAMP_MONOTONIC])
            + float(self.properties[DBUS_ATTR_LOADER_TIMESTAMP_MONOTONIC])
            + float(self.properties[DBUS_ATTR_KERNEL_TIMESTAMP_MONOTONIC])
            + float(self.properties[DBUS_ATTR_USERSPACE_TIMESTAMP_MONOTONIC])
        ) / 1e6

    @property
    @dbus_property
    def boot_timestamp(self) -> int:
        """Return the boot timestamp."""
        return self.properties[DBUS_ATTR_FINISH_TIMESTAMP]

    @dbus_connected
    async def reboot(self) -> None:
        """Reboot host computer."""
        await self.dbus.Manager.Reboot()

    @dbus_connected
    async def power_off(self) -> None:
        """Power off host computer."""
        await self.dbus.Manager.PowerOff()

    @dbus_connected
    async def start_unit(self, unit, mode) -> str:
        """Start a systemd service unit. Return job object path."""
        return (await self.dbus.Manager.StartUnit(unit, mode))[0]

    @dbus_connected
    async def stop_unit(self, unit, mode) -> str:
        """Stop a systemd service unit."""
        return (await self.dbus.Manager.StopUnit(unit, mode))[0]

    @dbus_connected
    async def reload_unit(self, unit, mode) -> str:
        """Reload a systemd service unit."""
        return (await self.dbus.Manager.ReloadOrRestartUnit(unit, mode))[0]

    @dbus_connected
    async def restart_unit(self, unit, mode):
        """Restart a systemd service unit."""
        return (await self.dbus.Manager.RestartUnit(unit, mode))[0]

    @dbus_connected
    async def list_units(
        self,
    ) -> list[str, str, str, str, str, str, str, int, str, str]:
        """Return a list of available systemd services."""
        return (await self.dbus.Manager.ListUnits())[0]

    @dbus_connected
    async def update(self):
        """Update Properties."""
        self.properties = await self.dbus.get_properties(DBUS_IFACE_SYSTEMD_MANAGER)
