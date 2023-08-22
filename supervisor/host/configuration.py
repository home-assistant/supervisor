"""Network objects for host manager."""

from dataclasses import dataclass
from ipaddress import IPv4Address, IPv4Interface, IPv6Address, IPv6Interface

from ..dbus.const import (
    ConnectionStateFlags,
    ConnectionStateType,
    DeviceType,
    InterfaceMethod as NMInterfaceMethod,
)
from ..dbus.network.connection import NetworkConnection
from ..dbus.network.interface import NetworkInterface
from .const import AuthMethod, InterfaceMethod, InterfaceType, WifiMode


@dataclass(slots=True)
class AccessPoint:
    """Represent a wifi configuration."""

    mode: WifiMode
    ssid: str
    mac: str
    frequency: int
    signal: int


@dataclass(slots=True)
class IpConfig:
    """Represent a IP configuration."""

    method: InterfaceMethod
    address: list[IPv4Interface | IPv6Interface]
    gateway: IPv4Address | IPv6Address | None
    nameservers: list[IPv4Address | IPv6Address]
    ready: bool | None


@dataclass(slots=True)
class WifiConfig:
    """Represent a wifi configuration."""

    mode: WifiMode
    ssid: str
    auth: AuthMethod
    psk: str | None
    signal: int | None


@dataclass(slots=True)
class VlanConfig:
    """Represent a vlan configuration."""

    id: int
    interface: str


@dataclass(slots=True)
class Interface:
    """Represent a host network interface."""

    name: str
    mac: str
    path: str
    enabled: bool
    connected: bool
    primary: bool
    type: InterfaceType
    ipv4: IpConfig | None
    ipv6: IpConfig | None
    wifi: WifiConfig | None
    vlan: VlanConfig | None

    def equals_dbus_interface(self, inet: NetworkInterface) -> bool:
        """Return true if this represents the dbus interface."""
        if not inet.settings:
            return False

        if inet.settings.match and inet.settings.match.path:
            return inet.settings.match.path == [self.path]

        return inet.settings.connection.interface_name == self.name

    @staticmethod
    def from_dbus_interface(inet: NetworkInterface) -> "Interface":
        """Coerce a dbus interface into normal Interface."""
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
            inet.hw_address,
            inet.path,
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
