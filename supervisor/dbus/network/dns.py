"""D-Bus interface for hostname."""
import logging
from typing import List, Optional

from ...exceptions import DBusError, DBusInterfaceError
from ...utils.gdbus import DBus
from ..interface import DBusInterface
from ..utils import dbus_connected
from .configuration import DNSConfiguration
from .const import DBUS_NAME_NM, DBUS_OBJECT_DNS

_LOGGER: logging.Logger = logging.getLogger(__name__)


class NetworkManagerDNS(DBusInterface):
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
        data = await self.dbus.get_properties(f"{DBUS_NAME_NM}.DnsManager")
        if not data:
            _LOGGER.warning("Can't get properties for NMI DnsManager")
            return

        self._mode = data.get("Mode")
        self._rc_manager = data.get("RcManager")

        # Parse configuraton
        self._configuration = [
            DNSConfiguration(x) for x in data.get("Configuration", [])
        ]
