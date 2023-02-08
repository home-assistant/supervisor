"""Network Manager implementation for DBUS."""
import logging
from typing import Any

from awesomeversion import AwesomeVersion, AwesomeVersionException
from dbus_fast.aio.message_bus import MessageBus

from ...exceptions import (
    DBusError,
    DBusFatalError,
    DBusInterfaceError,
    HostNotSupportedError,
)
from ...utils.sentry import capture_exception
from ..const import (
    DBUS_ATTR_CONNECTION_ENABLED,
    DBUS_ATTR_DEVICES,
    DBUS_ATTR_PRIMARY_CONNECTION,
    DBUS_ATTR_VERSION,
    DBUS_IFACE_NM,
    DBUS_NAME_NM,
    DBUS_OBJECT_BASE,
    DBUS_OBJECT_NM,
    ConnectivityState,
    DeviceType,
)
from ..interface import DBusInterfaceProxy, dbus_property
from ..utils import dbus_connected
from .connection import NetworkConnection
from .dns import NetworkManagerDNS
from .interface import NetworkInterface
from .setting import NetworkSetting
from .settings import NetworkManagerSettings

_LOGGER: logging.Logger = logging.getLogger(__name__)

MINIMAL_VERSION = AwesomeVersion("1.14.6")


class NetworkManager(DBusInterfaceProxy):
    """Handle D-Bus interface for Network Manager.

    https://developer.gnome.org/NetworkManager/stable/gdbus-org.freedesktop.NetworkManager.html
    """

    name: str = DBUS_NAME_NM
    bus_name: str = DBUS_NAME_NM
    object_path: str = DBUS_OBJECT_NM
    properties_interface: str = DBUS_IFACE_NM

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
            _,
            obj_active_con,
        ) = await self.dbus.call_add_and_activate_connection(
            settings, device_object, DBUS_OBJECT_BASE
        )

        active_con = NetworkConnection(obj_active_con)
        await active_con.connect(self.dbus.bus)
        return active_con.settings, active_con

    @dbus_connected
    async def check_connectivity(self, *, force: bool = False) -> ConnectivityState:
        """Check the connectivity of the host."""
        if force:
            return await self.dbus.call_check_connectivity()
        else:
            return await self.dbus.get_connectivity()

    async def connect(self, bus: MessageBus) -> None:
        """Connect to system's D-Bus."""
        _LOGGER.info("Load dbus interface %s", self.name)
        try:
            await super().connect(bus)
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
    async def update(self, changed: dict[str, Any] | None = None) -> None:
        """Update Properties."""
        await super().update(changed)

        if not changed and self.dns.is_connected:
            await self.dns.update()

        if changed and (
            DBUS_ATTR_DEVICES not in changed
            or {
                intr.object_path for intr in self.interfaces.values() if intr.managed
            }.issubset(set(changed[DBUS_ATTR_DEVICES]))
        ):
            # If none of our managed devices were removed then most likely this is just veths changing.
            # We don't care about veths and reprocessing all their changes can swamp a system when
            # docker is having issues. This does mean we may miss activation of a new managed device
            # in rare occaisions but we'll catch it on the next host update scheduled task.
            return

        interfaces = {}
        curr_devices = {intr.object_path: intr for intr in self.interfaces.values()}
        for device in self.properties[DBUS_ATTR_DEVICES]:
            if device in curr_devices and curr_devices[device].is_connected:
                interface = curr_devices[device]
                await interface.update()
            else:
                interface = NetworkInterface(self.dbus, device)

                # Connect to interface
                try:
                    await interface.connect(self.dbus.bus)
                except (DBusFatalError, DBusInterfaceError) as err:
                    # Docker creates and deletes interfaces quite often, sometimes
                    # this causes a race condition: A device disappears while we
                    # try to query it. Ignore those cases.
                    _LOGGER.debug("Can't process %s: %s", device, err)
                    continue
                except Exception as err:  # pylint: disable=broad-except
                    _LOGGER.exception("Error while processing %s: %s", device, err)
                    capture_exception(err)
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
            else:
                interface.primary = False

            interfaces[interface.name] = interface

        # Disconnect removed devices
        for device in set(curr_devices.keys()) - set(
            self.properties[DBUS_ATTR_DEVICES]
        ):
            curr_devices[device].shutdown()

        self._interfaces = interfaces

    def shutdown(self) -> None:
        """Shutdown the object and disconnect from D-Bus.

        This method is irreversible.
        """
        self.dns.shutdown()
        self.settings.shutdown()
        super().shutdown()

    def disconnect(self) -> None:
        """Disconnect from D-Bus."""
        for intr in self.interfaces.values():
            intr.shutdown()

        super().disconnect()
