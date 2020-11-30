"""Info control for host."""
from __future__ import annotations

import asyncio
from ipaddress import IPv4Address, IPv4Interface, IPv6Address, IPv6Interface
import logging
from typing import List, Optional, Union

import attr

from ..coresys import CoreSys, CoreSysAttributes
from ..dbus.const import (
    DBUS_NAME_NM_CONNECTION_ACTIVE_CHANGED,
    ConnectionStateType,
    DeviceType,
    InterfaceMethod as NMInterfaceMethod,
    WirelessMethodType,
)
from ..dbus.network.accesspoint import NetworkWirelessAP
from ..dbus.network.connection import NetworkConnection
from ..dbus.network.interface import NetworkInterface
from ..dbus.payloads.generate import interface_update_payload
from ..exceptions import (
    DBusError,
    DBusNotConnectedError,
    DBusProgramError,
    HostNetworkError,
    HostNetworkNotFound,
    HostNotSupportedError,
)
from .const import AuthMethod, InterfaceMethod, InterfaceType, WifiMode

_LOGGER: logging.Logger = logging.getLogger(__name__)


class NetworkManager(CoreSysAttributes):
    """Handle local network setup."""

    def __init__(self, coresys: CoreSys):
        """Initialize system center handling."""
        self.coresys: CoreSys = coresys
        self._connectivity: Optional[bool] = None

    @property
    def connectivity(self) -> Optional[bool]:
        """Return true current connectivity state."""
        return self._connectivity

    @property
    def interfaces(self) -> List[Interface]:
        """Return a dictionary of active interfaces."""
        interfaces: List[Interface] = []
        for inet in self.sys_dbus.network.interfaces.values():
            interfaces.append(Interface.from_dbus_interface(inet))

        return interfaces

    @property
    def dns_servers(self) -> List[str]:
        """Return a list of local DNS servers."""
        # Read all local dns servers
        servers: List[str] = []
        for config in self.sys_dbus.network.dns.configuration:
            if config.vpn or not config.nameservers:
                continue
            servers.extend(config.nameservers)

        return list(dict.fromkeys(servers))

    async def check_connectivity(self):
        """Check the internet connection.

        ConnectionState 4 == FULL (has internet)
        https://developer.gnome.org/NetworkManager/stable/nm-dbus-types.html#NMConnectivityState
        """
        if not self.sys_dbus.network.connectivity_enabled:
            return

        # Check connectivity
        try:
            state = await self.sys_dbus.network.check_connectivity()
            self._connectivity = state[0] == 4
        except DBusError as err:
            _LOGGER.warning("Can't update connectivity information: %s", err)
            self._connectivity = False

    def get(self, inet_name: str) -> Interface:
        """Return interface from interface name."""
        if inet_name not in self.sys_dbus.network.interfaces:
            raise HostNetworkNotFound()

        return Interface.from_dbus_interface(
            self.sys_dbus.network.interfaces[inet_name]
        )

    async def update(self):
        """Update properties over dbus."""
        _LOGGER.info("Updating local network information")
        try:
            await self.sys_dbus.network.update()
        except DBusError:
            _LOGGER.warning("Can't update network information!")
        except DBusNotConnectedError as err:
            _LOGGER.error("No network D-Bus connection available")
            raise HostNotSupportedError() from err

        await self.check_connectivity()

    async def apply_changes(self, interface: Interface) -> None:
        """Apply Interface changes to host."""
        inet = self.sys_dbus.network.interfaces.get(interface.name)

        # Update exist configuration
        if (
            inet
            and inet.settings
            and inet.settings.connection.interface_name == interface.name
            and interface.enabled
        ):
            settings = interface_update_payload(
                interface,
                name=inet.settings.connection.id,
                uuid=inet.settings.connection.uuid,
            )

            try:
                await inet.settings.update(settings)
                await self.sys_dbus.network.activate_connection(
                    inet.settings.object_path, inet.object_path
                )
            except DBusError as err:
                _LOGGER.error("Can't update config on %s: %s", interface.name, err)
                raise HostNetworkError() from err

        # Create new configuration and activate interface
        elif inet and interface.enabled:
            settings = interface_update_payload(interface)

            try:
                await self.sys_dbus.network.add_and_activate_connection(
                    settings, inet.object_path
                )
            except DBusError as err:
                _LOGGER.error(
                    "Can't create config and activate %s: %s", interface.name, err
                )
                raise HostNetworkError() from err

        # Remove config from interface
        elif inet and inet.settings and not interface.enabled:
            try:
                await inet.settings.delete()
            except DBusError as err:
                _LOGGER.error("Can't disable interface %s: %s", interface.name, err)
                raise HostNetworkError() from err

        # Create new interface (like vlan)
        elif not inet:
            settings = interface_update_payload(interface)

            try:
                await self.sys_dbus.network.settings.add_connection(settings)
            except DBusError as err:
                _LOGGER.error("Can't create new interface: %s", err)
                raise HostNetworkError() from err
        else:
            _LOGGER.warning("Requested Network interface update is not possible")
            raise HostNetworkError()

        await self.sys_dbus.network.dbus.wait_signal(
            DBUS_NAME_NM_CONNECTION_ACTIVE_CHANGED
        )
        await self.update()

    async def scan_wifi(self, interface: Interface) -> List[AccessPoint]:
        """Scan on Interface for AccessPoint."""
        inet = self.sys_dbus.network.interfaces.get(interface.name)

        if inet.type != DeviceType.WIRELESS:
            _LOGGER.error("Can only scan with wireless card - %s", interface.name)
            raise HostNotSupportedError()

        # Request Scan
        try:
            await inet.wireless.request_scan()
        except DBusProgramError as err:
            _LOGGER.debug("Can't request a new scan: %s", err)
        except DBusError as err:
            raise HostNetworkError() from err
        else:
            await asyncio.sleep(5)

        # Process AP
        accesspoints: List[AccessPoint] = []
        for ap_object in (await inet.wireless.get_all_accesspoints())[0]:
            accesspoint = NetworkWirelessAP(ap_object)

            try:
                await accesspoint.connect()
            except DBusError as err:
                _LOGGER.warning("Can't process an AP: %s", err)
                continue
            else:
                accesspoints.append(
                    AccessPoint(
                        WifiMode[WirelessMethodType(accesspoint.mode).name],
                        accesspoint.ssid,
                        accesspoint.mac,
                        accesspoint.frequency,
                        accesspoint.strength,
                    )
                )

        return accesspoints


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
    address: List[Union[IPv4Interface, IPv6Interface]] = attr.ib()
    gateway: Optional[Union[IPv4Address, IPv6Address]] = attr.ib()
    nameservers: List[Union[IPv4Address, IPv6Address]] = attr.ib()


@attr.s(slots=True)
class WifiConfig:
    """Represent a wifi configuration."""

    mode: WifiMode = attr.ib()
    ssid: str = attr.ib()
    auth: AuthMethod = attr.ib()
    psk: Optional[str] = attr.ib()
    signal: Optional[int] = attr.ib()


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
    ipv4: Optional[IpConfig] = attr.ib()
    ipv6: Optional[IpConfig] = attr.ib()
    wifi: Optional[WifiConfig] = attr.ib()
    vlan: Optional[VlanConfig] = attr.ib()

    @staticmethod
    def from_dbus_interface(inet: NetworkInterface) -> Interface:
        """Concert a dbus interface into normal Interface."""
        return Interface(
            inet.name,
            inet.settings is not None,
            Interface._map_nm_connected(inet.connection),
            inet.primary,
            Interface._map_nm_type(inet.type),
            IpConfig(
                Interface._map_nm_method(inet.settings.ipv4.method),
                inet.connection.ipv4.address,
                inet.connection.ipv4.gateway,
                inet.connection.ipv4.nameservers,
            )
            if inet.connection and inet.connection.ipv4
            else IpConfig(InterfaceMethod.DISABLED, [], None, []),
            IpConfig(
                Interface._map_nm_method(inet.settings.ipv6.method),
                inet.connection.ipv6.address,
                inet.connection.ipv6.gateway,
                inet.connection.ipv6.nameservers,
            )
            if inet.connection and inet.connection.ipv6
            else IpConfig(InterfaceMethod.DISABLED, [], None, []),
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
        }

        return mapping.get(method, InterfaceMethod.DISABLED)

    @staticmethod
    def _map_nm_connected(connection: Optional[NetworkConnection]) -> bool:
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
    def _map_nm_wifi(inet: NetworkInterface) -> Optional[WifiConfig]:
        """Create mapping to nm wifi property."""
        if inet.type != DeviceType.WIRELESS or not inet.settings:
            return None

        # Authentication
        auth = None
        if not inet.settings.wireless_security:
            auth = AuthMethod.OPEN
        if inet.settings.wireless_security.key_mgmt == "none":
            auth = AuthMethod.WEP
        elif inet.settings.wireless_security.key_mgmt == "wpa-psk":
            auth = AuthMethod.WPA_PSK

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
            inet.settings.wireless_security.psk,
            signal,
        )

    @staticmethod
    def _map_nm_vlan(inet: NetworkInterface) -> Optional[WifiConfig]:
        """Create mapping to nm vlan property."""
        if inet.type != DeviceType.VLAN or not inet.settings:
            return None

        return VlanConfig(inet.settings.vlan.id, inet.settings.vlan.parent)
