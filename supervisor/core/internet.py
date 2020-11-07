"""Internet object for the Supervisor."""
import asyncio

from aiohttp import ClientError

from ..const import URL_HASSIO_VERSION
from ..coresys import CoreSys, CoreSysAttributes


class CoreInternet(CoreSysAttributes):
    """Internet object for the Supervisor."""

    def __init__(self, coresys: CoreSys):
        """Initialize Supervisor object."""
        self.coresys = coresys
        self._connected = False

    @property
    def connected(self) -> bool:
        """Return true if we are connected to the internet."""
        return self._connected

    async def check_connection(self):
        """Check the connection."""
        try:
            await self.sys_websession.head(
                URL_HASSIO_VERSION.format(channel=self.sys_updater.channel), timeout=10
            )
        except (ClientError, asyncio.TimeoutError):
            self._connected = False
        else:
            self._connected = True
