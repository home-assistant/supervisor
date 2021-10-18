"""D-Bus interface for hostname."""
from ipaddress import ip_address
import logging
from typing import Optional

from ...const import (
    ATTR_DOMAINS,
    ATTR_INTERFACE,
    ATTR_NAMESERVERS,
    ATTR_PRIORITY,
    ATTR_VPN,
)
from ...exceptions import DBusError, DBusInterfaceError
from ...utils.dbus_next import DBus
from ..const import (
    DBUS_ATTR_CONFIGURATION,
    DBUS_ATTR_MODE,
    DBUS_ATTR_RCMANAGER,
    DBUS_NAME_DNS,
    DBUS_NAME_NM,
    DBUS_OBJECT_DNS,
)
from ..interface import DBusInterface
from ..utils import dbus_connected
from .configuration import DNSConfiguration

_LOGGER: logging.Logger = logging.getLogger(__name__)


class NetworkManagerDNS(DBusInterface):
    """Handle D-Bus interface for NMI DnsManager."""

    def __init__(self) -> None:
        """Initialize Properties."""
        self._mode: Optional[str] = None
        self._rc_manager: Optional[str] = None
        self._configuration: list[DNSConfiguration] = []

    @property
    def mode(self) -> Optional[str]:
        """Return Propertie mode."""
        return self._mode

    @property
    def rc_manager(self) -> Optional[str]:
        """Return Propertie RcManager."""
        return self._rc_manager

    @property
    def configuration(self) -> list[DNSConfiguration]:
        """Return Propertie configuraton."""
        return self._configuration

    async def connect(self) -> None:
        """Connect to system's D-Bus."""
        try:
            self.dbus = await DBus.connect(DBUS_NAME_NM, DBUS_OBJECT_DNS)
        except DBusError:
            _LOGGER.warning("Can't connect to DnsManager")
        except DBusInterfaceError:
            _LOGGER.warning(
                "No DnsManager support on the host. Local DNS functions have been disabled."
            )

    @dbus_connected
    async def update(self):
        """Update Properties."""
        data = await self.dbus.get_properties(DBUS_NAME_DNS)
        if not data:
            _LOGGER.warning("Can't get properties for DnsManager")
            return

        self._mode = data.get(DBUS_ATTR_MODE)
        self._rc_manager = data.get(DBUS_ATTR_RCMANAGER)

        # Parse configuraton
        self._configuration = [
            DNSConfiguration(
                [ip_address(nameserver) for nameserver in config.get(ATTR_NAMESERVERS)],
                config.get(ATTR_DOMAINS),
                config.get(ATTR_INTERFACE),
                config.get(ATTR_PRIORITY),
                config.get(ATTR_VPN),
            )
            for config in data.get(DBUS_ATTR_CONFIGURATION, [])
        ]
