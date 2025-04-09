"""NetworkConnection objects for Network Manager."""

from abc import ABC
from dataclasses import dataclass
from ipaddress import IPv4Address, IPv6Address


@dataclass(slots=True)
class DNSConfiguration:
    """DNS configuration Object."""

    nameservers: list[IPv4Address | IPv6Address]
    domains: list[str]
    interface: str
    priority: int
    vpn: bool


@dataclass(slots=True)
class ConnectionProperties:
    """Connection Properties object for Network Manager."""

    id: str | None
    uuid: str | None
    type: str | None
    interface_name: str | None


@dataclass(slots=True)
class WirelessProperties:
    """Wireless Properties object for Network Manager."""

    ssid: str
    assigned_mac: str | None
    mode: str | None
    powersave: int | None


@dataclass(slots=True)
class WirelessSecurityProperties:
    """Wireless Security Properties object for Network Manager."""

    auth_alg: str | None
    key_mgmt: str | None
    psk: str | None


@dataclass(slots=True)
class EthernetProperties:
    """Ethernet properties object for Network Manager."""

    assigned_mac: str | None


@dataclass(slots=True)
class VlanProperties:
    """Ethernet properties object for Network Manager."""

    id: int
    parent: str | None


@dataclass(slots=True)
class IpAddress:
    """IP address object for Network Manager."""

    address: str
    prefix: int


@dataclass
class IpProperties(ABC):
    """IP properties object for Network Manager."""

    method: str | None
    address_data: list[IpAddress] | None
    gateway: str | None


@dataclass(slots=True)
class Ip4Properties(IpProperties):
    """IP4 properties object."""

    dns: list[int] | None


@dataclass(slots=True)
class Ip6Properties(IpProperties):
    """IPv6 properties object for Network Manager."""

    addr_gen_mode: int
    ip6_privacy: int
    dns: list[bytes] | None


@dataclass(slots=True)
class MatchProperties:
    """Match properties object for Network Manager."""

    path: list[str] | None = None
