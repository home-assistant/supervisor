"""NetworkConnection object4s for Network Manager."""
from ipaddress import IPv4Address, IPv4Interface, IPv6Address, IPv6Interface
from typing import Optional, Union

import attr


@attr.s(slots=True)
class IpConfiguration:
    """NetworkSettingsIPConfig object for Network Manager."""

    gateway: Optional[Union[IPv6Address, IPv6Address]] = attr.ib()
    nameservers: list[Union[IPv6Address, IPv6Address]] = attr.ib()
    address: list[Union[IPv4Interface, IPv6Interface]] = attr.ib()


@attr.s(slots=True)
class DNSConfiguration:
    """DNS configuration Object."""

    nameservers: list[Union[IPv4Address, IPv6Address]] = attr.ib()
    domains: list[str] = attr.ib()
    interface: str = attr.ib()
    priority: int = attr.ib()
    vpn: bool = attr.ib()


@attr.s(slots=True)
class ConnectionProperties:
    """Connection Properties object for Network Manager."""

    id: Optional[str] = attr.ib()
    uuid: Optional[str] = attr.ib()
    type: Optional[str] = attr.ib()
    interface_name: Optional[str] = attr.ib()


@attr.s(slots=True)
class WirelessProperties:
    """Wireless Properties object for Network Manager."""

    ssid: Optional[str] = attr.ib()
    assigned_mac: Optional[str] = attr.ib()
    mode: Optional[str] = attr.ib()
    powersave: Optional[int] = attr.ib()


@attr.s(slots=True)
class WirelessSecurityProperties:
    """Wireless Security Properties object for Network Manager."""

    auth_alg: Optional[str] = attr.ib()
    key_mgmt: Optional[str] = attr.ib()
    psk: Optional[str] = attr.ib()


@attr.s(slots=True)
class EthernetProperties:
    """Ethernet properties object for Network Manager."""

    assigned_mac: Optional[str] = attr.ib()


@attr.s(slots=True)
class VlanProperties:
    """Ethernet properties object for Network Manager."""

    id: Optional[int] = attr.ib()
    parent: Optional[str] = attr.ib()


@attr.s(slots=True)
class IpProperties:
    """IP properties object for Network Manager."""

    method: Optional[str] = attr.ib()
