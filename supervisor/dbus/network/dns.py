"""Network Manager DNS Manager object."""

from ipaddress import ip_address
import logging
from typing import Any

from dbus_fast.aio.message_bus import MessageBus

from ...const import (
    ATTR_DOMAINS,
    ATTR_INTERFACE,
    ATTR_NAMESERVERS,
    ATTR_PRIORITY,
    ATTR_VPN,
)
from ...exceptions import DBusError, DBusInterfaceError, DBusServiceUnkownError
from ..const import (
    DBUS_ATTR_CONFIGURATION,
    DBUS_ATTR_MODE,
    DBUS_ATTR_RCMANAGER,
    DBUS_IFACE_DNS,
    DBUS_NAME_NM,
    DBUS_OBJECT_DNS,
)
from ..interface import DBusInterfaceProxy
from ..utils import dbus_connected
from .configuration import DNSConfiguration

_LOGGER: logging.Logger = logging.getLogger(__name__)


class NetworkManagerDNS(DBusInterfaceProxy):
    """Handle D-Bus interface for NM DnsManager.

    https://developer.gnome.org/NetworkManager/stable/gdbus-org.freedesktop.NetworkManager.DnsManager.html
    """

    bus_name: str = DBUS_NAME_NM
    object_path: str = DBUS_OBJECT_DNS
    properties_interface: str = DBUS_IFACE_DNS

    def __init__(self) -> None:
        """Initialize Properties."""
        super().__init__()

        self._mode: str | None = None
        self._rc_manager: str | None = None
        self._configuration: list[DNSConfiguration] = []

    @property
    def mode(self) -> str | None:
        """Return Propertie mode."""
        return self._mode

    @property
    def rc_manager(self) -> str | None:
        """Return Propertie RcManager."""
        return self._rc_manager

    @property
    def configuration(self) -> list[DNSConfiguration]:
        """Return Propertie configuraton."""
        return self._configuration

    async def connect(self, bus: MessageBus) -> None:
        """Connect to system's D-Bus."""
        try:
            await super().connect(bus)
        except DBusError:
            _LOGGER.warning("Can't connect to DnsManager")
        except (DBusServiceUnkownError, DBusInterfaceError):
            _LOGGER.warning(
                "No DnsManager support on the host. Local DNS functions have been disabled."
            )

    @dbus_connected
    async def update(self, changed: dict[str, Any] | None = None) -> None:
        """Update Properties."""
        await super().update(changed)
        if not self.properties:
            _LOGGER.warning("Can't get properties for DnsManager")
            return

        self._mode = self.properties.get(DBUS_ATTR_MODE)
        self._rc_manager = self.properties.get(DBUS_ATTR_RCMANAGER)

        # Parse configuraton
        if not changed or DBUS_ATTR_CONFIGURATION in changed:
            self._configuration = [
                DNSConfiguration(
                    [
                        ip_address(nameserver)
                        for nameserver in config.get(ATTR_NAMESERVERS)
                    ],
                    config.get(ATTR_DOMAINS),
                    config.get(ATTR_INTERFACE),
                    config.get(ATTR_PRIORITY),
                    config.get(ATTR_VPN),
                )
                for config in self.properties.get(DBUS_ATTR_CONFIGURATION, [])
            ]
