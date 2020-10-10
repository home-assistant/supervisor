"""NetworkConnection object4s for Network Manager."""
from typing import List

import attr

from ...utils.gdbus import DBus


class NetworkAttributes:
    """NetworkAttributes object for Network Manager."""

    def __init__(self, object_path: str, properties: dict) -> None:
        """Initialize NetworkAttributes object."""
        self._properties = properties
        self.object_path = object_path


@attr.s
class AddressData:
    """AddressData object for Network Manager."""

    address: str = attr.ib()
    prefix: int = attr.ib()


@attr.s
class IpConfiguration:
    """NetworkSettingsIPConfig object for Network Manager."""

    gateway: str = attr.ib()
    method: str = attr.ib()
    nameservers: List[int] = attr.ib()
    address_data: AddressData = attr.ib()


@attr.s
class DNSConfiguration:
    """DNS configuration Object."""

    nameservers: List[str] = attr.ib()
    domains: List[str] = attr.ib()
    interface: str = attr.ib()
    priority: int = attr.ib()
    vpn: bool = attr.ib()


@attr.s
class NetworkSettings:
    """NetworkSettings object for Network Manager."""

    dbus: DBus = attr.ib()


@attr.s
class NetworkDevice:
    """Device properties."""

    dbus: DBus = attr.ib()
    interface: str = attr.ib()
    ip4_address: int = attr.ib()
    device_type: int = attr.ib()
    real: bool = attr.ib()


@attr.s
class WirelessProperties:
    """WirelessProperties object for Network Manager."""

    properties: dict = attr.ib()
    security: dict = attr.ib()
    ssid: str = attr.ib()
