"""Service control for host."""
import logging

import attr

from ..coresys import CoreSysAttributes
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
        """Iterator trought services."""
        return iter(self._services)

    def _check_dbus(self, unit=None):
        """Check available dbus connection."""
        if not self.sys_dbus.systemd.is_connected:
            _LOGGER.error("No systemd dbus connection available")
            raise HostNotSupportedError()

        if unit and not self.exists(unit):
            _LOGGER.error("Unit '%s' not found", unit)
            raise HostServiceError()

    def start(self, unit):
        """Start a service on host."""
        self._check_dbus(unit)

        _LOGGER.info("Start local service %s", unit)
        return self.sys_dbus.systemd.start_unit(unit, MOD_REPLACE)

    def stop(self, unit):
        """Stop a service on host."""
        self._check_dbus(unit)

        _LOGGER.info("Stop local service %s", unit)
        return self.sys_dbus.systemd.stop_unit(unit, MOD_REPLACE)

    def reload(self, unit):
        """Reload a service on host."""
        self._check_dbus(unit)

        _LOGGER.info("Reload local service %s", unit)
        return self.sys_dbus.systemd.reload_unit(unit, MOD_REPLACE)

    def restart(self, unit):
        """Restart a service on host."""
        self._check_dbus(unit)

        _LOGGER.info("Restart local service %s", unit)
        return self.sys_dbus.systemd.restart_unit(unit, MOD_REPLACE)

    def exists(self, unit):
        """Check if a unit exists and return True."""
        for service in self._services:
            if unit == service.name:
                return True
        return False

    async def update(self):
        """Update properties over dbus."""
        self._check_dbus()

        _LOGGER.info("Update service information")
        self._services.clear()
        try:
            systemd_units = await self.sys_dbus.systemd.list_units()
            for service_data in systemd_units[0]:
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
