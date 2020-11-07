"""Info control for host."""
from __future__ import annotations

from ipaddress import IPv4Address, IPv4Interface, IPv6Address, IPv6Interface
import logging
from typing import List, Optional, Union

import attr

from ..coresys import CoreSys, CoreSysAttributes
from ..dbus.const import (
    ConnectionStateType,
    DeviceType,
    InterfaceMethod as NMInterfaceMethod,
)
from ..dbus.network.connection import NetworkConnection
from ..dbus.network.interface import NetworkInterface
from ..dbus.payloads.generate import interface_update_payload
from ..exceptions import (
    DBusError,
    DBusNotConnectedError,
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
            _LOGGER.error("No hostname D-Bus connection available")
            raise HostNotSupportedError() from err

    async def apply_changes(self, interface: Interface) -> None:
        """Apply Interface changes to host."""
        inet = self.sys_dbus.network.interfaces[interface.name]
        await inet.update_settings(interface_update_payload(interface))
        await self.update()


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
    privacy: Optional[bool] = attr.ib()
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
            Interface._map_nm_privacy(inet),
            Interface._map_nm_type(inet.type),
            IpConfig(
                Interface._map_nm_method(inet.settings.ipv4.method),
                inet.connection.ipv4.address,
                inet.connection.ipv4.gateway,
                inet.connection.ipv4.nameservers,
            )
            if inet.connection and inet.connection.ipv4
            else None,
            IpConfig(
                Interface._map_nm_method(inet.settings.ipv6.method),
                inet.connection.ipv6.address,
                inet.connection.ipv6.gateway,
                inet.connection.ipv6.nameservers,
            )
            if inet.connection and inet.connection.ipv6
            else None,
            Interface._map_nm_wifi(inet),
            Interface._map_nm_vlan(inet),
        )

    @staticmethod
    def _map_nm_method(method: str) -> InterfaceMethod:
        """Map IP interface method."""
        mapping = {
            NMInterfaceMethod.AUTO: InterfaceMethod.DHCP,
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

        # Wireless operation mode
        mode = (
            WifiMode(inet.settings.wireless.mode)
            if inet.settings.wireless.mode
            else WifiMode.INFRASTRUCTURE
        )

        # Authentication
        if inet.settings.wireless_security.key_mgmt == "none":
            auth = AuthMethod.WEB
        elif inet.settings.wireless_security.key_mgmt == "wpa-psk":
            auth = AuthMethod.WPA_PSK
        else:
            auth = AuthMethod.OPEN

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

    @staticmethod
    def _map_nm_privacy(inet: NetworkInterface) -> Optional[bool]:
        """Generate privancy flag."""
        if inet.type == DeviceType.ETHERNET:
            return not inet.settings.ethernet.assigned_mac in ("stable", None)

        if inet.type == DeviceType.WIRELESS:
            return not inet.settings.wireless.assigned_mac == "stable"

        return None
