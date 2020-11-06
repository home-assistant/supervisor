"""Network Manager implementation for DBUS."""
import logging
from typing import Dict

import sentry_sdk

from ...exceptions import DBusError, DBusFatalError, DBusInterfaceError
from ...utils.gdbus import DBus
from ..const import (
    DBUS_ATTR_ACTIVE_CONNECTIONS,
    DBUS_ATTR_PRIMARY_CONNECTION,
    DBUS_NAME_NM,
    DBUS_OBJECT_NM,
    ConnectionType,
)
from ..interface import DBusInterface
from ..utils import dbus_connected
from .dns import NetworkManagerDNS
from .interface import NetworkInterface

_LOGGER: logging.Logger = logging.getLogger(__name__)


class NetworkManager(DBusInterface):
    """Handle D-Bus interface for Network Manager."""

    def __init__(self) -> None:
        """Initialize Properties."""
        self._dns: NetworkManagerDNS = NetworkManagerDNS()
        self._interfaces: Dict[str, NetworkInterface] = {}

    @property
    def dns(self) -> NetworkManagerDNS:
        """Return NetworkManager DNS interface."""
        return self._dns

    @property
    def interfaces(self) -> Dict[str, NetworkInterface]:
        """Return a dictionary of active interfaces."""
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

        self._interfaces.clear()
        for connection in data.get(DBUS_ATTR_ACTIVE_CONNECTIONS, []):
            interface = NetworkInterface(self.dbus)

            await interface.connect(connection)

            if interface.connection.type not in [
                ConnectionType.ETHERNET,
                ConnectionType.WIRELESS,
                ConnectionType.VLAN,
            ]:
                continue

            # Process data
            try:
                await interface.connection.update_information()
            except (DBusFatalError):
                continue
            except (KeyError, IndexError, ValueError) as err:
                _LOGGER.warning("Error while processing interface: %s", err)
                sentry_sdk.capture_exception(err)
                continue

            if interface.connection.device.driver in ("veth", "bridge", "tun"):
                continue

            if interface.connection.object_path == data.get(
                DBUS_ATTR_PRIMARY_CONNECTION
            ):
                interface.connection.primary = True

            self._interfaces[interface.connection.device.interface] = interface
