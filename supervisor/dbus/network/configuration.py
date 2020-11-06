"""NetworkConnection object4s for Network Manager."""
from ipaddress import IPv4Address, IPv4Interface, IPv6Address, IPv6Interface
from typing import List, Optional, Union

import attr

from ...utils.gdbus import DBus
from ..const import InterfaceMethod


class NetworkAttributes:
    """NetworkAttributes object for Network Manager."""

    def __init__(self, object_path: str, properties: dict) -> None:
        """Initialize NetworkAttributes object."""
        self._properties = properties
        self.object_path = object_path


@attr.s(slots=True)
class IpConfiguration:
    """NetworkSettingsIPConfig object for Network Manager."""

    gateway: Optional[Union[IPv6Address, IPv6Address]] = attr.ib()
    method: InterfaceMethod = attr.ib()
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
class NetworkSettings:
    """NetworkSettings object for Network Manager."""

    dbus: DBus = attr.ib()


@attr.s(slots=True)
class NetworkDevice:
    """Device properties."""

    dbus: DBus = attr.ib()
    interface: str = attr.ib()
    device_type: int = attr.ib()
    real: bool = attr.ib()
    driver: str = attr.ib()


@attr.s(slots=True)
class WirelessProperties:
    """WirelessProperties object for Network Manager."""

    dbus: DBus = attr.ib()
    properties: dict = attr.ib()
    security: dict = attr.ib()
    ssid: str = attr.ib()


@attr.s(slots=True)
class EthernetProperties:
    """Ethernet properties object for Network Manager."""

    properties: dict = attr.ib()
