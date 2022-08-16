"""NetworkConnection object4s for Network Manager."""
from ipaddress import IPv4Address, IPv4Interface, IPv6Address, IPv6Interface

import attr


@attr.s(slots=True)
class IpConfiguration:
    """NetworkSettingsIPConfig object for Network Manager."""

    gateway: IPv6Address | IPv6Address | None = attr.ib()
    nameservers: list[IPv6Address | IPv6Address] = attr.ib()
    address: list[IPv4Interface | IPv6Interface] = attr.ib()


@attr.s(slots=True)
class DNSConfiguration:
    """DNS configuration Object."""

    nameservers: list[IPv4Address | IPv6Address] = attr.ib()
    domains: list[str] = attr.ib()
    interface: str = attr.ib()
    priority: int = attr.ib()
    vpn: bool = attr.ib()


@attr.s(slots=True)
class ConnectionProperties:
    """Connection Properties object for Network Manager."""

    id: str | None = attr.ib()
    uuid: str | None = attr.ib()
    type: str | None = attr.ib()
    interface_name: str | None = attr.ib()


@attr.s(slots=True)
class WirelessProperties:
    """Wireless Properties object for Network Manager."""

    ssid: str | None = attr.ib()
    assigned_mac: str | None = attr.ib()
    mode: str | None = attr.ib()
    powersave: int | None = attr.ib()


@attr.s(slots=True)
class WirelessSecurityProperties:
    """Wireless Security Properties object for Network Manager."""

    auth_alg: str | None = attr.ib()
    key_mgmt: str | None = attr.ib()
    psk: str | None = attr.ib()


@attr.s(slots=True)
class EthernetProperties:
    """Ethernet properties object for Network Manager."""

    assigned_mac: str | None = attr.ib()


@attr.s(slots=True)
class VlanProperties:
    """Ethernet properties object for Network Manager."""

    id: int | None = attr.ib()
    parent: str | None = attr.ib()


@attr.s(slots=True)
class IpProperties:
    """IP properties object for Network Manager."""

    method: str | None = attr.ib()
