"""Interface to Systemd over D-Bus."""
import logging
from typing import Any

from ..exceptions import DBusError, DBusInterfaceError
from ..utils.gdbus import DBus
from .const import (
    DBUS_ATTR_FINISH_TIMESTAMP,
    DBUS_ATTR_FIRMWARE_TIMESTAMP_MONOTONIC,
    DBUS_ATTR_KERNEL_TIMESTAMP_MONOTONIC,
    DBUS_ATTR_LOADER_TIMESTAMP_MONOTONIC,
    DBUS_ATTR_USERSPACE_TIMESTAMP_MONOTONIC,
    DBUS_NAME_SYSTEMD_MANAGER,
    DBUS_NAME_SYSTEMD,
    DBUS_OBJECT_SYSTEMD,
)
from .interface import DBusInterface, dbus_property
from .utils import dbus_connected

_LOGGER: logging.Logger = logging.getLogger(__name__)


class Systemd(DBusInterface):
    """Systemd function handler."""

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
    def reboot(self):
        """Reboot host computer.

        Return a coroutine.
        """
        return self.dbus.Manager.Reboot()

    @dbus_connected
    def power_off(self):
        """Power off host computer.

        Return a coroutine.
        """
        return self.dbus.Manager.PowerOff()

    @dbus_connected
    def start_unit(self, unit, mode):
        """Start a systemd service unit.

        Return a coroutine.
        """
        return self.dbus.Manager.StartUnit(unit, mode)

    @dbus_connected
    def stop_unit(self, unit, mode):
        """Stop a systemd service unit.

        Return a coroutine.
        """
        return self.dbus.Manager.StopUnit(unit, mode)

    @dbus_connected
    def reload_unit(self, unit, mode):
        """Reload a systemd service unit.

        Return a coroutine.
        """
        return self.dbus.Manager.ReloadOrRestartUnit(unit, mode)

    @dbus_connected
    def restart_unit(self, unit, mode):
        """Restart a systemd service unit.

        Return a coroutine.
        """
        return self.dbus.Manager.RestartUnit(unit, mode)

    @dbus_connected
    def list_units(self):
        """Return a list of available systemd services.

        Return a coroutine.
        """
        return self.dbus.Manager.ListUnits()

    @dbus_connected
    async def update(self):
        """Update Properties."""
        self.properties = await self.dbus.get_properties(DBUS_NAME_SYSTEMD_MANAGER)
