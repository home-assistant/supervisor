"""Info control for host."""
from __future__ import annotations

from ipaddress import IPv4Address, IPv4Interface, IPv6Address, IPv6Interface
import logging
from typing import List, Union

import attr

from ..coresys import CoreSys, CoreSysAttributes
from ..dbus.const import ConnectionType
from ..dbus.network.interface import NetworkInterface
from ..exceptions import (
    DBusError,
    DBusNotConnectedError,
    HostNetworkNotFound,
    HostNotSupportedError,
)
from .const import InterfaceMode

_LOGGER: logging.Logger = logging.getLogger(__name__)


@attr.s(slots=True)
class IpConfig:
    """Represent a IP configuration."""

    mode: InterfaceMode = attr.ib()
    address: List[Union[IPv4Interface, IPv6Interface]] = attr.ib()
    gateway: Union[IPv4Address, IPv6Address] = attr.ib()
    nameservers: List[Union[IPv4Address, IPv6Address]] = attr.ib()


@attr.s(slots=True)
class Interface:
    """Represent a host network interface."""

    id: str = attr.ib()
    name: str = attr.ib()
    primary: bool = attr.ib()
    type: ConnectionType = attr.ib()
    ipv4: IpConfig = attr.ib()
    ipv6: IpConfig = attr.ib()

    @staticmethod
    def from_dbus_interface(inet: NetworkInterface) -> Interface:
        """Concert a dbus interface into normal Interface."""
        return Interface(
            inet.connection.id,
            inet.connection.device.interface,
            inet.connection.primary,
            inet.connection.type,
            IpConfig(
                MAP_NM_METHOD[inet.connection.ip4_config.method],
                inet.connection.ip4_config.address,
                inet.connection.ip4_config.gateway,
                inet.connection.ip4_config.nameservers,
            ),
            IpConfig(
                MAP_NM_METHOD[inet.connection.ip6_config.method],
                inet.connection.ip6_config.address,
                inet.connection.ip6_config.gateway,
                inet.connection.ip6_config.nameservers,
            ),
        )


MAP_NM_METHOD = {
    "auto": InterfaceMode.DHCP,
    "disabled": InterfaceMode.DISABLE,
    None: InterfaceMode.STATIC,
}


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
        if inet_name in self.sys_dbus.network.interfaces:
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
