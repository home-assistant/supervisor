"""Network Manager implementation for DBUS."""
import asyncio
import logging
from typing import Any

from awesomeversion import AwesomeVersion, AwesomeVersionException
from dbus_next.aio.message_bus import MessageBus
import sentry_sdk

from ...exceptions import (
    DBusError,
    DBusFatalError,
    DBusInterfaceError,
    DBusInterfaceMethodError,
    HostNotSupportedError,
)
from ...utils.dbus import DBus
from ..const import (
    DBUS_ATTR_CONNECTION_ENABLED,
    DBUS_ATTR_DEVICES,
    DBUS_ATTR_PRIMARY_CONNECTION,
    DBUS_ATTR_VERSION,
    DBUS_IFACE_NM,
    DBUS_NAME_NM,
    DBUS_OBJECT_BASE,
    DBUS_OBJECT_NM,
    DeviceType,
)
from ..interface import DBusInterface, dbus_property
from ..utils import dbus_connected
from .connection import NetworkConnection
from .dns import NetworkManagerDNS
from .interface import NetworkInterface
from .setting import NetworkSetting
from .settings import NetworkManagerSettings

_LOGGER: logging.Logger = logging.getLogger(__name__)

MINIMAL_VERSION = AwesomeVersion("1.14.6")


class NetworkManager(DBusInterface):
    """Handle D-Bus interface for Network Manager.

    https://developer.gnome.org/NetworkManager/stable/gdbus-org.freedesktop.NetworkManager.html
    """

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
    @dbus_property
    def connectivity_enabled(self) -> bool:
        """Return if connectivity check is enabled."""
        return self.properties[DBUS_ATTR_CONNECTION_ENABLED]

    @property
    @dbus_property
    def version(self) -> AwesomeVersion:
        """Return Network Manager version."""
        return AwesomeVersion(self.properties[DBUS_ATTR_VERSION])

    @dbus_connected
    async def activate_connection(
        self, connection_object: str, device_object: str
    ) -> NetworkConnection:
        """Activate a connction on a device."""
        obj_active_con = await self.dbus.call_activate_connection(
            connection_object, device_object, DBUS_OBJECT_BASE
        )
        active_con = NetworkConnection(obj_active_con)
        await active_con.connect(self.dbus.bus)
        return active_con

    @dbus_connected
    async def add_and_activate_connection(
        self, settings: Any, device_object: str
    ) -> tuple[NetworkSetting, NetworkConnection]:
        """Activate a connction on a device."""
        (
            obj_con_setting,
            obj_active_con,
        ) = await self.dbus.call_add_and_activate_connection(
            settings, device_object, DBUS_OBJECT_BASE
        )

        con_setting = NetworkSetting(obj_con_setting)
        active_con = NetworkConnection(obj_active_con)
        await asyncio.gather(
            con_setting.connect(self.dbus.bus), active_con.connect(self.dbus.bus)
        )
        return con_setting, active_con

    @dbus_connected
    async def check_connectivity(self, *, force: bool = False) -> int:
        """Check the connectivity of the host."""
        if force:
            return await self.dbus.call_check_connectivity()
        else:
            return await self.dbus.get_connectivity()

    async def connect(self, bus: MessageBus) -> None:
        """Connect to system's D-Bus."""
        try:
            self.dbus = await DBus.connect(bus, DBUS_NAME_NM, DBUS_OBJECT_NM)
            await self.dns.connect(bus)
            await self.settings.connect(bus)
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
        self.properties = await self.dbus.get_properties(DBUS_IFACE_NM)

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
        self.properties = await self.dbus.get_properties(DBUS_IFACE_NM)

        await self.dns.update()

        self._interfaces.clear()
        for device in self.properties[DBUS_ATTR_DEVICES]:
            interface = NetworkInterface(self.dbus, device)

            # Connect to interface
            try:
                await interface.connect(self.dbus.bus)
            except (DBusFatalError, DBusInterfaceMethodError) as err:
                # Docker creates and deletes interfaces quite often, sometimes
                # this causes a race condition: A device disappears while we
                # try to query it. Ignore those cases.
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
