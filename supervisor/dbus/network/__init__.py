"""Network Manager implementation for DBUS."""
import logging
from typing import Any, Awaitable

from awesomeversion import AwesomeVersion, AwesomeVersionException
import sentry_sdk

from ...exceptions import (
    DBusError,
    DBusInterfaceError,
    DBusProgramError,
    HostNotSupportedError,
)
from ...utils.gdbus import DBus
from ..const import (
    DBUS_ATTR_CONNECTION_ENABLED,
    DBUS_ATTR_DEVICES,
    DBUS_ATTR_PRIMARY_CONNECTION,
    DBUS_ATTR_VERSION,
    DBUS_NAME_NM,
    DBUS_OBJECT_BASE,
    DBUS_OBJECT_NM,
    DeviceType,
)
from ..interface import DBusInterface
from ..utils import dbus_connected
from .dns import NetworkManagerDNS
from .interface import NetworkInterface
from .settings import NetworkManagerSettings

_LOGGER: logging.Logger = logging.getLogger(__name__)

MINIMAL_VERSION = AwesomeVersion("1.14.6")


class NetworkManager(DBusInterface):
    """Handle D-Bus interface for Network Manager."""

    name = DBUS_NAME_NM

    def __init__(self) -> None:
        """Initialize Properties."""
        self._dns: NetworkManagerDNS = NetworkManagerDNS()
        self._settings: NetworkManagerSettings = NetworkManagerSettings()
        self._interfaces: dict[str, NetworkInterface] = {}

        self.properties: dict[str, Any] = {}

    @property
    def dns(self) -> NetworkManagerDNS:
        """Return NetworkManager DNS interface."""
        return self._dns

    @property
    def settings(self) -> NetworkManagerSettings:
        """Return NetworkManager global settings."""
        return self._settings

    @property
    def interfaces(self) -> dict[str, NetworkInterface]:
        """Return a dictionary of active interfaces."""
        return self._interfaces

    @property
    def connectivity_enabled(self) -> bool:
        """Return if connectivity check is enabled."""
        return self.properties[DBUS_ATTR_CONNECTION_ENABLED]

    @property
    def version(self) -> AwesomeVersion:
        """Return if connectivity check is enabled."""
        return AwesomeVersion(self.properties[DBUS_ATTR_VERSION])

    @dbus_connected
    def activate_connection(
        self, connection_object: str, device_object: str
    ) -> Awaitable[Any]:
        """Activate a connction on a device."""
        return self.dbus.ActivateConnection(
            ("o", connection_object), ("o", device_object), ("o", DBUS_OBJECT_BASE)
        )

    @dbus_connected
    def add_and_activate_connection(
        self, settings: Any, device_object: str
    ) -> Awaitable[Any]:
        """Activate a connction on a device."""
        return self.dbus.AddAndActivateConnection(
            ("a{sa{sv}}", settings), ("o", device_object), ("o", DBUS_OBJECT_BASE)
        )

    @dbus_connected
    async def check_connectivity(self) -> Awaitable[Any]:
        """Check the connectivity of the host."""
        return await self.dbus.CheckConnectivity()

    async def connect(self) -> None:
        """Connect to system's D-Bus."""
        try:
            self.dbus = await DBus.connect(DBUS_NAME_NM, DBUS_OBJECT_NM)
            await self.dns.connect()
            await self.settings.connect()
        except DBusError:
            _LOGGER.warning("Can't connect to Network Manager")
        except DBusInterfaceError:
            _LOGGER.warning(
                "No Network Manager support on the host. Local network functions have been disabled."
            )

        # Make Sure we only connect to supported version
        if self.is_connected:
            try:
                await self._validate_version()
            except (HostNotSupportedError, DBusError):
                self.disconnect()
                self.dns.disconnect()
                self.settings.disconnect()

    async def _validate_version(self) -> None:
        """Validate Version of NetworkManager."""
        self.properties = await self.dbus.get_properties(DBUS_NAME_NM)

        try:
            if self.version >= MINIMAL_VERSION:
                return
        except (AwesomeVersionException, KeyError):
            pass

        raise HostNotSupportedError(
            f"Version '{self.version}' of NetworkManager is not supported!",
            _LOGGER.error,
        )

    @dbus_connected
    async def update(self):
        """Update Properties."""
        self.properties = await self.dbus.get_properties(DBUS_NAME_NM)

        await self.dns.update()

        self._interfaces.clear()
        for device in self.properties[DBUS_ATTR_DEVICES]:
            interface = NetworkInterface(self.dbus, device)

            # Connect to interface
            try:
                await interface.connect()
            except DBusProgramError as err:
                _LOGGER.warning("Can't process %s: %s", device, err)
                continue
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.exception("Error while processing interface: %s", err)
                sentry_sdk.capture_exception(err)
                continue

            # Skeep interface
            if (
                interface.type
                not in [
                    DeviceType.ETHERNET,
                    DeviceType.WIRELESS,
                    DeviceType.VLAN,
                ]
                or not interface.managed
            ):
                continue

            if (
                interface.connection
                and interface.connection.object_path
                == self.properties[DBUS_ATTR_PRIMARY_CONNECTION]
            ):
                interface.primary = True

            self._interfaces[interface.name] = interface
