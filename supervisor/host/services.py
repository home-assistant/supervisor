"""Service control for host."""

from collections.abc import Awaitable
import logging

import attr

from ..coresys import CoreSysAttributes
from ..dbus.const import StartUnitMode, StopUnitMode
from ..exceptions import HassioError, HostNotSupportedError, HostServiceError

_LOGGER: logging.Logger = logging.getLogger(__name__)

MOD_REPLACE = "replace"


class ServiceManager(CoreSysAttributes):
    """Handle local service information controls."""

    def __init__(self, coresys):
        """Initialize system center handling."""
        self.coresys = coresys
        self._services = set()

    def __iter__(self):
        """Iterate through services."""
        return iter(self._services)

    def _check_dbus(self, unit=None):
        """Check available dbus connection."""
        if not self.sys_dbus.systemd.is_connected:
            raise HostNotSupportedError(
                "No systemd D-Bus connection available", _LOGGER.error
            )

        if unit and not self.exists(unit):
            raise HostServiceError(f"Unit '{unit}' not found", _LOGGER.error)

    def start(self, unit) -> Awaitable[str]:
        """Start a service on host.

        Returns a coroutine.
        """
        self._check_dbus(unit)

        _LOGGER.info("Starting local service %s", unit)
        return self.sys_dbus.systemd.start_unit(unit, StartUnitMode.REPLACE)

    def stop(self, unit) -> Awaitable[str]:
        """Stop a service on host.

        Returns a coroutine.
        """
        self._check_dbus(unit)

        _LOGGER.info("Stopping local service %s", unit)
        return self.sys_dbus.systemd.stop_unit(unit, StopUnitMode.REPLACE)

    def reload(self, unit) -> Awaitable[str]:
        """Reload a service on host.

        Returns a coroutine.
        """
        self._check_dbus(unit)

        _LOGGER.info("Reloading local service %s", unit)
        return self.sys_dbus.systemd.reload_unit(unit, StartUnitMode.REPLACE)

    def restart(self, unit) -> Awaitable[str]:
        """Restart a service on host.

        Returns a coroutine.
        """
        self._check_dbus(unit)

        _LOGGER.info("Restarting local service %s", unit)
        return self.sys_dbus.systemd.restart_unit(unit, StartUnitMode.REPLACE)

    def exists(self, unit) -> bool:
        """Check if a unit exists and return True."""
        for service in self._services:
            if unit == service.name:
                return True
        return False

    async def update(self):
        """Update properties over dbus."""
        self._check_dbus()

        _LOGGER.info("Updating service information")
        self._services.clear()
        try:
            systemd_units = await self.sys_dbus.systemd.list_units()
            for service_data in systemd_units:
                if (
                    not service_data[0].endswith(".service")
                    or service_data[2] != "loaded"
                ):
                    continue
                self._services.add(ServiceInfo.read_from(service_data))
        except (HassioError, IndexError):
            _LOGGER.warning("Can't update host service information!")


@attr.s(frozen=True)
class ServiceInfo:
    """Represent a single Service."""

    name: str = attr.ib()
    description: str = attr.ib()
    state: str = attr.ib()

    @staticmethod
    def read_from(unit):
        """Parse data from D-Bus into this object."""
        return ServiceInfo(unit[0], unit[1], unit[3])
