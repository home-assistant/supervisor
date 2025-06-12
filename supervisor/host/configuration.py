"""Network objects for host manager."""

from dataclasses import dataclass
from ipaddress import IPv4Address, IPv4Interface, IPv6Address, IPv6Interface
import logging
import socket

from ..dbus.const import (
    ConnectionStateFlags,
    ConnectionStateType,
    DeviceType,
    InterfaceAddrGenMode as NMInterfaceAddrGenMode,
    InterfaceIp6Privacy as NMInterfaceIp6Privacy,
    InterfaceMethod as NMInterfaceMethod,
)
from ..dbus.network.connection import NetworkConnection
from ..dbus.network.interface import NetworkInterface
from .const import (
    AuthMethod,
    InterfaceAddrGenMode,
    InterfaceIp6Privacy,
    InterfaceMethod,
    InterfaceType,
    WifiMode,
)

_LOGGER: logging.Logger = logging.getLogger(__name__)


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
    """Represent a (current) IP configuration."""

    address: list[IPv4Interface | IPv6Interface]
    gateway: IPv4Address | IPv6Address | None
    nameservers: list[IPv4Address | IPv6Address]
    ready: bool | None


@dataclass(slots=True)
class IpSetting:
    """Represent a user IP setting."""

    method: InterfaceMethod
    address: list[IPv4Interface | IPv6Interface]
    gateway: IPv4Address | IPv6Address | None
    nameservers: list[IPv4Address | IPv6Address]


@dataclass(slots=True)
class Ip6Setting(IpSetting):
    """Represent a user IPv6 setting."""

    addr_gen_mode: InterfaceAddrGenMode = InterfaceAddrGenMode.DEFAULT
    ip6_privacy: InterfaceIp6Privacy = InterfaceIp6Privacy.DEFAULT


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
    interface: str | None


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
    ipv4setting: IpSetting | None
    ipv6: IpConfig | None
    ipv6setting: Ip6Setting | None
    wifi: WifiConfig | None
    vlan: VlanConfig | None

    def equals_dbus_interface(self, inet: NetworkInterface) -> bool:
        """Return true if this represents the dbus interface."""
        if not inet.settings:
            return False

        if inet.settings.match and inet.settings.match.path:
            return inet.settings.match.path == [self.path]

        return (
            inet.settings.connection is not None
            and inet.settings.connection.interface_name == self.name
        )

    @staticmethod
    def from_dbus_interface(inet: NetworkInterface) -> "Interface":
        """Coerce a dbus interface into normal Interface."""
        if inet.settings and inet.settings.ipv4:
            ipv4_setting = IpSetting(
                method=Interface._map_nm_method(inet.settings.ipv4.method),
                address=[
                    IPv4Interface(f"{ip.address}/{ip.prefix}")
                    for ip in inet.settings.ipv4.address_data
                ]
                if inet.settings.ipv4.address_data
                else [],
                gateway=IPv4Address(inet.settings.ipv4.gateway)
                if inet.settings.ipv4.gateway
                else None,
                nameservers=[
                    IPv4Address(socket.ntohl(ip)) for ip in inet.settings.ipv4.dns
                ]
                if inet.settings.ipv4.dns
                else [],
            )
        else:
            ipv4_setting = IpSetting(InterfaceMethod.DISABLED, [], None, [])

        if inet.settings and inet.settings.ipv6:
            ipv6_setting = Ip6Setting(
                method=Interface._map_nm_method(inet.settings.ipv6.method),
                addr_gen_mode=Interface._map_nm_addr_gen_mode(
                    inet.settings.ipv6.addr_gen_mode
                ),
                ip6_privacy=Interface._map_nm_ip6_privacy(
                    inet.settings.ipv6.ip6_privacy
                ),
                address=[
                    IPv6Interface(f"{ip.address}/{ip.prefix}")
                    for ip in inet.settings.ipv6.address_data
                ]
                if inet.settings.ipv6.address_data
                else [],
                gateway=IPv6Address(inet.settings.ipv6.gateway)
                if inet.settings.ipv6.gateway
                else None,
                nameservers=[IPv6Address(bytes(ip)) for ip in inet.settings.ipv6.dns]
                if inet.settings.ipv6.dns
                else [],
            )
        else:
            ipv6_setting = Ip6Setting(InterfaceMethod.DISABLED, [], None, [])

        ipv4_ready = (
            inet.connection is not None
            and ConnectionStateFlags.IP4_READY in inet.connection.state_flags
        )
        ipv6_ready = (
            inet.connection is not None
            and ConnectionStateFlags.IP6_READY in inet.connection.state_flags
        )

        return Interface(
            name=inet.name,
            mac=inet.hw_address,
            path=inet.path,
            enabled=inet.settings is not None,
            connected=Interface._map_nm_connected(inet.connection),
            primary=inet.primary,
            type=Interface._map_nm_type(inet.type),
            ipv4=IpConfig(
                address=inet.connection.ipv4.address
                if inet.connection.ipv4.address
                else [],
                gateway=inet.connection.ipv4.gateway,
                nameservers=inet.connection.ipv4.nameservers
                if inet.connection.ipv4.nameservers
                else [],
                ready=ipv4_ready,
            )
            if inet.connection and inet.connection.ipv4
            else IpConfig([], None, [], ipv4_ready),
            ipv4setting=ipv4_setting,
            ipv6=IpConfig(
                address=inet.connection.ipv6.address
                if inet.connection.ipv6.address
                else [],
                gateway=inet.connection.ipv6.gateway,
                nameservers=inet.connection.ipv6.nameservers
                if inet.connection.ipv6.nameservers
                else [],
                ready=ipv6_ready,
            )
            if inet.connection and inet.connection.ipv6
            else IpConfig([], None, [], ipv6_ready),
            ipv6setting=ipv6_setting,
            wifi=Interface._map_nm_wifi(inet),
            vlan=Interface._map_nm_vlan(inet),
        )

    @staticmethod
    def _map_nm_method(method: str | None) -> InterfaceMethod:
        """Map IP interface method."""
        match method:
            case NMInterfaceMethod.AUTO.value:
                return InterfaceMethod.AUTO
            case NMInterfaceMethod.MANUAL:
                return InterfaceMethod.STATIC
        return InterfaceMethod.DISABLED

    @staticmethod
    def _map_nm_addr_gen_mode(addr_gen_mode: int) -> InterfaceAddrGenMode:
        """Map IPv6 interface addr_gen_mode."""
        mapping = {
            NMInterfaceAddrGenMode.EUI64.value: InterfaceAddrGenMode.EUI64,
            NMInterfaceAddrGenMode.STABLE_PRIVACY.value: InterfaceAddrGenMode.STABLE_PRIVACY,
            NMInterfaceAddrGenMode.DEFAULT_OR_EUI64.value: InterfaceAddrGenMode.DEFAULT_OR_EUI64,
        }

        return mapping.get(addr_gen_mode, InterfaceAddrGenMode.DEFAULT)

    @staticmethod
    def _map_nm_ip6_privacy(ip6_privacy: int) -> InterfaceIp6Privacy:
        """Map IPv6 interface ip6_privacy."""
        mapping = {
            NMInterfaceIp6Privacy.DISABLED.value: InterfaceIp6Privacy.DISABLED,
            NMInterfaceIp6Privacy.ENABLED_PREFER_PUBLIC.value: InterfaceIp6Privacy.ENABLED_PREFER_PUBLIC,
            NMInterfaceIp6Privacy.ENABLED.value: InterfaceIp6Privacy.ENABLED,
        }

        return mapping.get(ip6_privacy, InterfaceIp6Privacy.DEFAULT)

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
        match device_type:
            case DeviceType.ETHERNET.value:
                return InterfaceType.ETHERNET
            case DeviceType.WIRELESS.value:
                return InterfaceType.WIRELESS
            case DeviceType.VLAN.value:
                return InterfaceType.VLAN
        raise ValueError(f"Invalid device type: {device_type}")

    @staticmethod
    def _map_nm_wifi(inet: NetworkInterface) -> WifiConfig | None:
        """Create mapping to nm wifi property."""
        if inet.type != DeviceType.WIRELESS or not inet.settings:
            return None

        # Authentication and PSK
        auth = AuthMethod.OPEN
        psk = None
        if inet.settings.wireless_security:
            match inet.settings.wireless_security.key_mgmt:
                case "none":
                    auth = AuthMethod.WEP
                case "wpa-psk":
                    auth = AuthMethod.WPA_PSK
                    psk = inet.settings.wireless_security.psk
                case _:
                    _LOGGER.warning(
                        "Auth method %s for network interface %s unsupported, skipping",
                        inet.settings.wireless_security.key_mgmt,
                        inet.name,
                    )
                    return None

        # WifiMode
        mode = WifiMode.INFRASTRUCTURE
        if inet.settings.wireless and inet.settings.wireless.mode:
            mode = WifiMode(inet.settings.wireless.mode)

        # Signal
        if inet.wireless and inet.wireless.active:
            signal = inet.wireless.active.strength
        else:
            signal = None

        return WifiConfig(
            mode=mode,
            ssid=inet.settings.wireless.ssid if inet.settings.wireless else "",
            auth=auth,
            psk=psk,
            signal=signal,
        )

    @staticmethod
    def _map_nm_vlan(inet: NetworkInterface) -> VlanConfig | None:
        """Create mapping to nm vlan property."""
        if inet.type != DeviceType.VLAN or not inet.settings or not inet.settings.vlan:
            return None

        return VlanConfig(inet.settings.vlan.id, inet.settings.vlan.parent)
