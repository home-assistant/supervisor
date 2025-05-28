"""Info control for host."""

import asyncio
from contextlib import suppress
import logging
from typing import Any

from ..const import ATTR_HOST_INTERNET
from ..coresys import CoreSys, CoreSysAttributes
from ..dbus.const import (
    DBUS_ATTR_CONNECTION_ENABLED,
    DBUS_ATTR_CONNECTIVITY,
    DBUS_ATTR_PRIMARY_CONNECTION,
    DBUS_IFACE_NM,
    DBUS_OBJECT_BASE,
    DBUS_SIGNAL_NM_CONNECTION_ACTIVE_CHANGED,
    ConnectionStateType,
    ConnectivityState,
    DeviceType,
    WirelessMethodType,
)
from ..dbus.network.connection import NetworkConnection
from ..dbus.network.interface import NetworkInterface
from ..dbus.network.setting.generate import get_connection_from_interface
from ..exceptions import (
    DBusError,
    DBusNotConnectedError,
    HostNetworkError,
    HostNetworkNotFound,
    HostNotSupportedError,
    NetworkInterfaceNotFound,
)
from ..jobs.const import JobCondition
from ..jobs.decorator import Job
from ..resolution.checks.network_interface_ipv4 import CheckNetworkInterfaceIPV4
from .configuration import AccessPoint, Interface
from .const import InterfaceMethod, WifiMode

_LOGGER: logging.Logger = logging.getLogger(__name__)


class NetworkManager(CoreSysAttributes):
    """Handle local network setup."""

    def __init__(self, coresys: CoreSys):
        """Initialize system center handling."""
        self.coresys: CoreSys = coresys
        self._connectivity: bool | None = None

    @property
    def connectivity(self) -> bool | None:
        """Return true current connectivity state."""
        return self._connectivity

    @connectivity.setter
    def connectivity(self, state: bool | None) -> None:
        """Set host connectivity state."""
        if self._connectivity == state:
            return

        if state is None or self._connectivity is None:
            self.sys_create_task(
                self.sys_resolution.evaluate.get("connectivity_check")()
            )

        self._connectivity = state
        self.sys_homeassistant.websocket.supervisor_update_event(
            "network", {ATTR_HOST_INTERNET: state}
        )
        if state and not self.sys_supervisor.connectivity:
            self.sys_create_task(self.sys_supervisor.check_connectivity())

    @property
    def interfaces(self) -> list[Interface]:
        """Return a dictionary of active interfaces."""
        interfaces: list[Interface] = []
        for inet in self.sys_dbus.network.interfaces:
            interfaces.append(Interface.from_dbus_interface(inet))

        return interfaces

    @property
    def dns_servers(self) -> list[str]:
        """Return a list of local DNS servers."""
        # Read all local dns servers
        servers: list[str] = []
        for config in self.sys_dbus.network.dns.configuration:
            if config.vpn or not config.nameservers:
                continue
            servers.extend(config.nameservers)

        return list(dict.fromkeys(servers))

    async def check_connectivity(self, *, force: bool = False):
        """Check the internet connection."""
        if not self.sys_dbus.network.connectivity_enabled:
            self.connectivity = None
            return

        # Check connectivity
        try:
            state = await self.sys_dbus.network.check_connectivity(force=force)
            self.connectivity = state == ConnectivityState.CONNECTIVITY_FULL
        except DBusError as err:
            _LOGGER.warning("Can't update connectivity information: %s", err)
            self.connectivity = False

    def get(self, inet_name: str) -> Interface:
        """Return interface from interface name."""
        if inet_name not in self.sys_dbus.network:
            raise HostNetworkNotFound()

        return Interface.from_dbus_interface(self.sys_dbus.network.get(inet_name))

    @Job(
        name="network_manager_load",
        conditions=[JobCondition.HOST_NETWORK],
        internal=True,
    )
    async def load(self):
        """Load network information and reapply defaults over dbus."""
        # Apply current settings on each interface so OS can update any out of date defaults
        interfaces = [
            Interface.from_dbus_interface(interface)
            for interface in self.sys_dbus.network.interfaces
            if not CheckNetworkInterfaceIPV4.check_interface(interface)
        ]
        with suppress(HostNetworkNotFound):
            await asyncio.gather(
                *[
                    self.apply_changes(interface, update_only=True)
                    for interface in interfaces
                    if interface.enabled
                    and (
                        interface.ipv4setting.method != InterfaceMethod.DISABLED
                        or interface.ipv6setting.method != InterfaceMethod.DISABLED
                    )
                ]
            )

        self.sys_dbus.network.dbus.properties.on_properties_changed(
            self._check_connectivity_changed
        )

    async def _check_connectivity_changed(
        self, interface: str, changed: dict[str, Any], invalidated: list[str]
    ):
        """Check if connectivity property has changed."""
        if interface != DBUS_IFACE_NM:
            return

        connectivity_check: bool | None = changed.get(DBUS_ATTR_CONNECTION_ENABLED)
        connectivity: int | None = changed.get(DBUS_ATTR_CONNECTIVITY)

        # This potentially updated the DNS configuration. Make sure the DNS plug-in
        # picks up the latest settings.
        if (
            DBUS_ATTR_PRIMARY_CONNECTION in changed
            and changed[DBUS_ATTR_PRIMARY_CONNECTION]
            and changed[DBUS_ATTR_PRIMARY_CONNECTION] != DBUS_OBJECT_BASE
            and await self.sys_plugins.dns.is_running()
        ):
            await self.sys_plugins.dns.restart()

        if (
            connectivity_check is True
            or DBUS_ATTR_CONNECTION_ENABLED in invalidated
            or DBUS_ATTR_CONNECTIVITY in invalidated
        ):
            self.sys_create_task(self.check_connectivity())

        elif connectivity_check is False:
            self.connectivity = None

        elif connectivity is not None:
            self.connectivity = connectivity == ConnectivityState.CONNECTIVITY_FULL

    async def update(self, *, force_connectivity_check: bool = False):
        """Update properties over dbus."""
        _LOGGER.info("Updating local network information")
        try:
            await self.sys_dbus.network.update()
        except DBusError:
            _LOGGER.warning("Can't update network information!")
        except DBusNotConnectedError as err:
            raise HostNotSupportedError(
                "No network D-Bus connection available", _LOGGER.error
            ) from err

        await self.check_connectivity(force=force_connectivity_check)

    async def apply_changes(
        self, interface: Interface, *, update_only: bool = False
    ) -> None:
        """Apply Interface changes to host."""
        inet: NetworkInterface | None = None
        with suppress(NetworkInterfaceNotFound):
            inet = self.sys_dbus.network.get(interface.name)

        con: NetworkConnection = None

        # Update exist configuration
        if inet and interface.equals_dbus_interface(inet) and interface.enabled:
            _LOGGER.debug("Updating existing configuration for %s", interface.name)
            settings = get_connection_from_interface(
                interface,
                self.sys_dbus.network,
                name=inet.settings.connection.id,
                uuid=inet.settings.connection.uuid,
            )

            try:
                await inet.settings.update(settings)
                con = await self.sys_dbus.network.activate_connection(
                    inet.settings.object_path, inet.object_path
                )
                _LOGGER.debug(
                    "activate_connection returns %s",
                    con.object_path,
                )
            except DBusError as err:
                raise HostNetworkError(
                    f"Can't update config on {interface.name}: {err}", _LOGGER.error
                ) from err

        # Stop if only updates are allowed as other paths create/delete interfaces
        elif update_only:
            raise HostNetworkNotFound(
                f"Requested to update interface {interface.name} which does not exist or is disabled.",
                _LOGGER.warning,
            )

        # Create new configuration and activate interface
        elif inet and interface.enabled:
            _LOGGER.debug("Create new configuration for %s", interface.name)
            settings = get_connection_from_interface(interface, self.sys_dbus.network)

            try:
                settings, con = await self.sys_dbus.network.add_and_activate_connection(
                    settings, inet.object_path
                )
                _LOGGER.debug(
                    "add_and_activate_connection returns %s",
                    con.object_path,
                )
            except DBusError as err:
                raise HostNetworkError(
                    f"Can't create config and activate {interface.name}: {err}",
                    _LOGGER.error,
                ) from err

        # Remove config from interface
        elif inet and not interface.enabled:
            if not inet.settings:
                _LOGGER.debug("Interface %s is already disabled.", interface.name)
                return
            try:
                await inet.settings.delete()
            except DBusError as err:
                raise HostNetworkError(
                    f"Can't disable interface {interface.name}: {err}", _LOGGER.error
                ) from err

        # Create new interface (like vlan)
        elif not inet:
            settings = get_connection_from_interface(interface, self.sys_dbus.network)

            try:
                await self.sys_dbus.network.settings.add_connection(settings)
            except DBusError as err:
                raise HostNetworkError(
                    f"Can't create new interface: {err}", _LOGGER.error
                ) from err
        else:
            raise HostNetworkError(
                "Requested Network interface update is not possible", _LOGGER.warning
            )

        if con:
            async with con.dbus.signal(
                DBUS_SIGNAL_NM_CONNECTION_ACTIVE_CHANGED
            ) as signal:
                # From this point we monitor signals. However, it might be that
                # the state change before this point. Get the state currently to
                # avoid any race condition.
                await con.update()
                state: ConnectionStateType = con.state

                while state != ConnectionStateType.ACTIVATED:
                    if state == ConnectionStateType.DEACTIVATED:
                        raise HostNetworkError(
                            "Activating connection failed, check connection settings."
                        )

                    msg = await signal.wait_for_signal()
                    state = msg[0]
                    _LOGGER.debug("Active connection state changed to %s", state)

        # update_only means not done by user so don't force a check afterwards
        await self.update(force_connectivity_check=not update_only)

    async def scan_wifi(self, interface: Interface) -> list[AccessPoint]:
        """Scan on Interface for AccessPoint."""
        inet = self.sys_dbus.network.get(interface.name)

        if inet.type != DeviceType.WIRELESS:
            raise HostNotSupportedError(
                f"Can only scan with wireless card - {interface.name}", _LOGGER.error
            )

        # Request Scan
        try:
            await inet.wireless.request_scan()
        except DBusError as err:
            _LOGGER.warning("Can't request a new scan: %s", err)
            raise HostNetworkError() from err

        await asyncio.sleep(5)

        # Process AP
        return [
            AccessPoint(
                WifiMode[WirelessMethodType(accesspoint.mode).name],
                accesspoint.ssid,
                accesspoint.mac,
                accesspoint.frequency,
                accesspoint.strength,
            )
            for accesspoint in await inet.wireless.get_all_accesspoints()
            if accesspoint.dbus
        ]
