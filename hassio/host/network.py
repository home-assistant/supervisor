"""Info control for host."""
import logging
from typing import List, Set

from ..coresys import CoreSysAttributes, CoreSys
from ..exceptions import HostNotSupportedError, DBusNotConnectedError, DBusError

_LOGGER: logging.Logger = logging.getLogger(__name__)


class NetworkManager(CoreSysAttributes):
    """Handle local network setup."""

    def __init__(self, coresys: CoreSys):
        """Initialize system center handling."""
        self.coresys: CoreSys = coresys

    @property
    def dns_servers(self) -> List[str]:
        """Return a list of local DNS servers."""
        # Read all local dns servers
        servers: Set[str] = set()
        for config in self.sys_dbus.nmi_dns.configuration:
            if config.vpn:
                continue
            servers |= set(config.servers)

        return [f"dns://{server}" for server in servers]

    async def update(self):
        """Update properties over dbus."""
        _LOGGER.info("Update local network DNS information")
        try:
            await self.sys_dbus.nmi_dns.update()
        except DBusError:
            _LOGGER.warning("Can't update host DNS system information!")
        except DBusNotConnectedError:
            _LOGGER.error("No hostname D-Bus connection available")
            raise HostNotSupportedError() from None
