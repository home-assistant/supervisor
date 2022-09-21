"""Info control for host."""
from __future__ import annotations

import asyncio
from contextlib import suppress
from ipaddress import IPv4Address, IPv4Interface, IPv6Address, IPv6Interface
import logging
from typing import Any

import attr

from ..const import ATTR_HOST_INTERNET
from ..coresys import CoreSys, CoreSysAttributes
from ..dbus.const import (
    DBUS_ATTR_CONNECTION_ENABLED,
    DBUS_ATTR_CONNECTIVITY,
    DBUS_IFACE_NM,
    DBUS_SIGNAL_NM_CONNECTION_ACTIVE_CHANGED,
    ConnectionStateFlags,
    ConnectionStateType,
    ConnectivityState,
    DeviceType,
    InterfaceMethod as NMInterfaceMethod,
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
)
from ..jobs.const import JobCondition
from ..jobs.decorator import Job
from ..resolution.checks.network_interface_ipv4 import CheckNetworkInterfaceIPV4
from .const import AuthMethod, InterfaceMethod, InterfaceType, WifiMode

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

    @property
    def interfaces(self) -> list[Interface]:
        """Return a dictionary of active interfaces."""
        interfaces: list[Interface] = []
        for inet in self.sys_dbus.network.interfaces.values():
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
        if inet_name not in self.sys_dbus.network.interfaces:
            raise HostNetworkNotFound()

        return Interface.from_dbus_interface(
            self.sys_dbus.network.interfaces[inet_name]
        )

    @Job(conditions=JobCondition.HOST_NETWORK)
    async def load(self):
        """Load network information and reapply defaults over dbus."""
        # Apply current settings on each interface so OS can update any out of date defaults
        interfaces = [
            Interface.from_dbus_interface(interface)
            for interface in self.sys_dbus.network.interfaces.values()
            if not CheckNetworkInterfaceIPV4.check_interface(interface)
        ]
        with suppress(HostNetworkNotFound):
            await asyncio.gather(
                *[
                    self.apply_changes(interface, update_only=True)
                    for interface in interfaces
                    if interface.enabled
                    and (
                        interface.ipv4.method != InterfaceMethod.DISABLED
                        or interface.ipv6.method != InterfaceMethod.DISABLED
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
        connectivity: bool | None = changed.get(DBUS_ATTR_CONNECTIVITY)

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
        inet = self.sys_dbus.network.interfaces.get(interface.name)
        con: NetworkConnection = None

        # Update exist configuration
        if (
            inet
            and inet.settings
            and inet.settings.connection.interface_name == interface.name
            and interface.enabled
        ):
            _LOGGER.debug("Updating existing configuration for %s", interface.name)
            settings = get_connection_from_interface(
                interface,
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
            settings = get_connection_from_interface(interface)

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
        elif inet and inet.settings and not interface.enabled:
            try:
                await inet.settings.delete()
            except DBusError as err:
                raise HostNetworkError(
                    f"Can't disable interface {interface.name}: {err}", _LOGGER.error
                ) from err

        # Create new interface (like vlan)
        elif not inet:
            settings = get_connection_from_interface(interface)

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
        inet = self.sys_dbus.network.interfaces.get(interface.name)

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
        else:
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


@attr.s(slots=True)
class AccessPoint:
    """Represent a wifi configuration."""

    mode: WifiMode = attr.ib()
    ssid: str = attr.ib()
    mac: str = attr.ib()
    frequency: int = attr.ib()
    signal: int = attr.ib()


@attr.s(slots=True)
class IpConfig:
    """Represent a IP configuration."""

    method: InterfaceMethod = attr.ib()
    address: list[IPv4Interface | IPv6Interface] = attr.ib()
    gateway: IPv4Address | IPv6Address | None = attr.ib()
    nameservers: list[IPv4Address | IPv6Address] = attr.ib()
    ready: bool | None = attr.ib()


@attr.s(slots=True)
class WifiConfig:
    """Represent a wifi configuration."""

    mode: WifiMode = attr.ib()
    ssid: str = attr.ib()
    auth: AuthMethod = attr.ib()
    psk: str | None = attr.ib()
    signal: int | None = attr.ib()


@attr.s(slots=True)
class VlanConfig:
    """Represent a vlan configuration."""

    id: int = attr.ib()
    interface: str = attr.ib()


@attr.s(slots=True)
class Interface:
    """Represent a host network interface."""

    name: str = attr.ib()
    enabled: bool = attr.ib()
    connected: bool = attr.ib()
    primary: bool = attr.ib()
    type: InterfaceType = attr.ib()
    ipv4: IpConfig | None = attr.ib()
    ipv6: IpConfig | None = attr.ib()
    wifi: WifiConfig | None = attr.ib()
    vlan: VlanConfig | None = attr.ib()

    @staticmethod
    def from_dbus_interface(inet: NetworkInterface) -> Interface:
        """Concert a dbus interface into normal Interface."""
        ipv4_method = (
            Interface._map_nm_method(inet.settings.ipv4.method)
            if inet.settings and inet.settings.ipv4
            else InterfaceMethod.DISABLED
        )
        ipv6_method = (
            Interface._map_nm_method(inet.settings.ipv6.method)
            if inet.settings and inet.settings.ipv6
            else InterfaceMethod.DISABLED
        )
        ipv4_ready = (
            bool(inet.connection)
            and ConnectionStateFlags.IP4_READY in inet.connection.state_flags
        )
        ipv6_ready = (
            bool(inet.connection)
            and ConnectionStateFlags.IP6_READY in inet.connection.state_flags
        )
        return Interface(
            inet.name,
            inet.settings is not None,
            Interface._map_nm_connected(inet.connection),
            inet.primary,
            Interface._map_nm_type(inet.type),
            IpConfig(
                ipv4_method,
                inet.connection.ipv4.address if inet.connection.ipv4.address else [],
                inet.connection.ipv4.gateway,
                inet.connection.ipv4.nameservers
                if inet.connection.ipv4.nameservers
                else [],
                ipv4_ready,
            )
            if inet.connection and inet.connection.ipv4
            else IpConfig(ipv4_method, [], None, [], ipv4_ready),
            IpConfig(
                ipv6_method,
                inet.connection.ipv6.address if inet.connection.ipv6.address else [],
                inet.connection.ipv6.gateway,
                inet.connection.ipv6.nameservers
                if inet.connection.ipv6.nameservers
                else [],
                ipv6_ready,
            )
            if inet.connection and inet.connection.ipv6
            else IpConfig(ipv6_method, [], None, [], ipv6_ready),
            Interface._map_nm_wifi(inet),
            Interface._map_nm_vlan(inet),
        )

    @staticmethod
    def _map_nm_method(method: str) -> InterfaceMethod:
        """Map IP interface method."""
        mapping = {
            NMInterfaceMethod.AUTO: InterfaceMethod.AUTO,
            NMInterfaceMethod.DISABLED: InterfaceMethod.DISABLED,
            NMInterfaceMethod.MANUAL: InterfaceMethod.STATIC,
            NMInterfaceMethod.LINK_LOCAL: InterfaceMethod.DISABLED,
        }

        return mapping.get(method, InterfaceMethod.DISABLED)

    @staticmethod
    def _map_nm_connected(connection: NetworkConnection | None) -> bool:
        """Map connectivity state."""
        if not connection:
            return False

        return connection.state in (
            ConnectionStateType.ACTIVATED,
            ConnectionStateType.ACTIVATING,
        )

    @staticmethod
    def _map_nm_type(device_type: int) -> InterfaceType:
        mapping = {
            DeviceType.ETHERNET: InterfaceType.ETHERNET,
            DeviceType.WIRELESS: InterfaceType.WIRELESS,
            DeviceType.VLAN: InterfaceType.VLAN,
        }
        return mapping[device_type]

    @staticmethod
    def _map_nm_wifi(inet: NetworkInterface) -> WifiConfig | None:
        """Create mapping to nm wifi property."""
        if inet.type != DeviceType.WIRELESS or not inet.settings:
            return None

        # Authentication and PSK
        auth = None
        psk = None
        if not inet.settings.wireless_security:
            auth = AuthMethod.OPEN
        elif inet.settings.wireless_security.key_mgmt == "none":
            auth = AuthMethod.WEP
        elif inet.settings.wireless_security.key_mgmt == "wpa-psk":
            auth = AuthMethod.WPA_PSK
            psk = inet.settings.wireless_security.psk

        # WifiMode
        mode = WifiMode.INFRASTRUCTURE
        if inet.settings.wireless.mode:
            mode = WifiMode(inet.settings.wireless.mode)

        # Signal
        if inet.wireless:
            signal = inet.wireless.active.strength
        else:
            signal = None

        return WifiConfig(
            mode,
            inet.settings.wireless.ssid,
            auth,
            psk,
            signal,
        )

    @staticmethod
    def _map_nm_vlan(inet: NetworkInterface) -> WifiConfig | None:
        """Create mapping to nm vlan property."""
        if inet.type != DeviceType.VLAN or not inet.settings:
            return None

        return VlanConfig(inet.settings.vlan.id, inet.settings.vlan.parent)
