"""NetworkConnection object4s for Network Manager."""
from typing import List

import attr


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
    address_data: List[AddressData] = attr.ib()


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

    flags: int = attr.ib()
    unsaved: bool = attr.ib()
    filename: str = attr.ib()
