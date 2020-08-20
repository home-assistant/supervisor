"""Network Manager implementation for DBUS."""
import logging
from typing import List, Optional

from ...exceptions import DBusError, DBusInterfaceError
from ...utils.gdbus import DBus
from ..interface import DBusInterface
from ..utils import dbus_connected
from .const import (
    ATTR_ACTIVE_CONNECTIONS,
    ATTR_PRIMARY_CONNECTION,
    DBUS_NAME_NM,
    DBUS_OBJECT_NM,
)
from .dns import NetworkManagerDNS
from .interface import NetworkInterface

_LOGGER = logging.getLogger(__name__)


class NetworkManager(DBusInterface):
    """Handle D-Bus interface for Network Manager."""

    def __init__(self) -> None:
        """Initialize Properties."""
        self._dns: NetworkManagerDNS = NetworkManagerDNS()
        self._interfaces: Optional[List[NetworkInterface]] = None

    @property
    def dns(self) -> NetworkManagerDNS:
        """Return NetworkManager DNS interface."""
        return self._dns

    @property
    def interfaces(self) -> List[NetworkInterface]:
        """Return a list of active interfaces."""
        return self._interfaces

    async def connect(self) -> None:
        """Connect to system's D-Bus."""
        try:
            self.dbus = await DBus.connect(DBUS_NAME_NM, DBUS_OBJECT_NM)
            await self.dns.connect()
        except DBusError:
            _LOGGER.warning("Can't connect to Network Manager")
        except DBusInterfaceError:
            _LOGGER.warning(
                "No Network Manager support on the host. Local network functions have been disabled."
            )

    @dbus_connected
    async def update(self):
        """Update Properties."""
        await self.dns.update()

        data = await self.dbus.get_properties(DBUS_NAME_NM)

        if not data:
            _LOGGER.warning("Can't get properties for Network Manager")
            return

        self._interfaces = []
        for connection in data.get(ATTR_ACTIVE_CONNECTIONS, []):
            interface = NetworkInterface()

            await interface.connect(self.dbus, connection)

            if not interface.connection.default:
                continue

            await interface.connection.update_information()

            if interface.connection.object_path == data.get(ATTR_PRIMARY_CONNECTION):
                interface.connection.primary = True

            self._interfaces.append(interface)

        _LOGGER.info(self.interfaces[0].connection.ip4_config.address_data.address)
