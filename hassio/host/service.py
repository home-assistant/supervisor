"""Service control for host."""
import logging

import attr

from ..coresys import CoreSysAttributes
from ..exceptions import HassioError, HostNotSupportedError

_LOGGER = logging.getLogger(__name__)


class ServiceManager(CoreSysAttributes):
    """Handle local service information controls."""

    def __init__(self, coresys):
        """Initialize system center handling."""
        self.coresys = coresys
        self._data = set()

    def _check_dbus(self):
        """Check available dbus connection."""
        if self.sys_dbus.systemd.is_connected:
            return

        _LOGGER.error("No systemd dbus connection available")
        raise HostNotSupportedError()

    @property
    def services(self):
        """Return a list of local services."""
        return self._data

    async def update(self):
        """Update properties over dbus."""
        self._check_dbus()

        _LOGGER.info("Update service information")
        try:
            systemd_units = await self.sys_dbus.systemd.list_units()
            for service_data in systemd_units[0]:
                self._data.add(ServiceInfo.read_from(service_data))
        except (HassioError, IndexError):
            _LOGGER.warning("Can't update host service information!")


@attr.s(frozen=True)
class ServiceInfo:
    """Represent a single Service."""

    name = attr.ib(type=str)
    description = attr.ib(type=str)
    state = attr.ib(type=str)
    object = attr.ib(type=str)

    @staticmethod
    def read_from(unit):
        """Parse data from dbus into this object."""
        return ServiceInfo(
            unit[0],
            unit[1],
            unit[3],
            unit[6]
        )
