"""Info control for host."""
import logging
from typing import Dict, List

from supervisor.dbus.network.interface import NetworkInterface

from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import DBusError, DBusNotConnectedError, HostNotSupportedError

_LOGGER: logging.Logger = logging.getLogger(__name__)


class NetworkManager(CoreSysAttributes):
    """Handle local network setup."""

    def __init__(self, coresys: CoreSys):
        """Initialize system center handling."""
        self.coresys: CoreSys = coresys

    @property
    def interfaces(self) -> Dict[str, NetworkInterface]:
        """Return a dictionary of active interfaces."""
        return self.sys_dbus.network.interfaces

    @property
    def dns_servers(self) -> List[str]:
        """Return a list of local DNS servers."""
        # Read all local dns servers
        servers: List[str] = []
        for config in self.sys_dbus.network.dns.configuration:
            if config.vpn or not config.nameservers:
                continue
            servers.extend(config.nameservers)

        return [f"dns://{server}" for server in list(dict.fromkeys(servers))]

    async def update(self):
        """Update properties over dbus."""
        _LOGGER.info("Update local network information")
        try:
            await self.sys_dbus.network.update()
        except DBusError:
            _LOGGER.warning("Can't update network information!")
        except DBusNotConnectedError as err:
            _LOGGER.error("No hostname D-Bus connection available")
            raise HostNotSupportedError() from err
