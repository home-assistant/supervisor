"""NetworkConnection object4s for Network Manager."""
from ipaddress import IPv4Address, IPv4Interface, IPv6Address, IPv6Interface
from typing import List, Optional, Union

import attr

from ...utils.gdbus import DBus


@attr.s(slots=True)
class IpConfiguration:
    """NetworkSettingsIPConfig object for Network Manager."""

    gateway: Optional[Union[IPv6Address, IPv6Address]] = attr.ib()
    nameservers: List[Union[IPv6Address, IPv6Address]] = attr.ib()
    address: List[Union[IPv4Interface, IPv6Interface]] = attr.ib()


@attr.s(slots=True)
class DNSConfiguration:
    """DNS configuration Object."""

    nameservers: List[Union[IPv4Address, IPv6Address]] = attr.ib()
    domains: List[str] = attr.ib()
    interface: str = attr.ib()
    priority: int = attr.ib()
    vpn: bool = attr.ib()


@attr.s(slots=True)
class WirelessProperties:
    """WirelessProperties object for Network Manager."""

    properties: dict = attr.ib()
    security: dict = attr.ib()
    ssid: str = attr.ib()


@attr.s(slots=True)
class EthernetProperties:
    """Ethernet properties object for Network Manager."""

    properties: dict = attr.ib()
