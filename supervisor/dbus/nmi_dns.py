"""D-Bus interface for hostname."""
import logging
from typing import List, Optional

import attr

from ..exceptions import DBusError, DBusInterfaceError
from ..utils.gdbus import DBus
from .interface import DBusInterface
from .utils import dbus_connected

_LOGGER: logging.Logger = logging.getLogger(__name__)

DBUS_NAME = "org.freedesktop.NetworkManager"
DBUS_OBJECT = "/org/freedesktop/NetworkManager/DnsManager"


@attr.s
class DNSConfiguration:
    """NMI DnsManager configuration Object."""

    nameservers: List[str] = attr.ib()
    domains: List[str] = attr.ib()
    interface: str = attr.ib()
    priority: int = attr.ib()
    vpn: bool = attr.ib()


class NMIDnsManager(DBusInterface):
    """Handle D-Bus interface for NMI DnsManager."""

    def __init__(self) -> None:
        """Initialize Properties."""
        self._mode: Optional[str] = None
        self._rc_manager: Optional[str] = None
        self._configuration: List[DNSConfiguration] = []

    @property
    def mode(self) -> Optional[str]:
        """Return Propertie mode."""
        return self._mode

    @property
    def rc_manager(self) -> Optional[str]:
        """Return Propertie RcManager."""
        return self._rc_manager

    @property
    def configuration(self) -> List[DNSConfiguration]:
        """Return Propertie configuraton."""
        return self._configuration

    async def connect(self) -> None:
        """Connect to system's D-Bus."""
        try:
            self.dbus = await DBus.connect(DBUS_NAME, DBUS_OBJECT)
        except DBusError:
            _LOGGER.warning("Can't connect to DnsManager")
        except DBusInterfaceError:
            _LOGGER.warning(
                "No DnsManager support on the host. Local DNS functions have been disabled."
            )

    @dbus_connected
    async def update(self):
        """Update Properties."""
        data = await self.dbus.get_properties(f"{DBUS_NAME}.DnsManager")
        if not data:
            _LOGGER.warning("Can't get properties for NMI DnsManager")
            return

        self._mode = data.get("Mode")
        self._rc_manager = data.get("RcManager")

        # Parse configuraton
        self._configuration.clear()
        for config in data.get("Configuration", []):
            dns = DNSConfiguration(
                config.get("nameservers"),
                config.get("domains"),
                config.get("interface"),
                config.get("priority"),
                config.get("vpn"),
            )
            self._configuration.append(dns)
